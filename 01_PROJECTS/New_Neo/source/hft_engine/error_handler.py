"""
Comprehensive Error Handling and Recovery System
"""
import asyncio
import logging
from datetime import datetime
import traceback
from functools import wraps


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling for the HFT engine"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
        self.circuit_breakers = {}
        self.max_retries = 3
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60  # seconds
    
    def record_error(self, component, error):
        """Record an error for a component"""
        error_key = f"{component}_{type(error).__name__}"
        
        # Update error counts
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Store last error
        self.last_errors[component] = {
            'error': str(error),
            'type': type(error).__name__,
            'timestamp': datetime.utcnow(),
            'traceback': traceback.format_exc()
        }
        
        logger.error(f"Error in {component}: {error}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Check circuit breaker
        if self.error_counts[error_key] >= self.circuit_breaker_threshold:
            self.activate_circuit_breaker(component)
    
    def activate_circuit_breaker(self, component):
        """Activate circuit breaker for a component"""
        if component not in self.circuit_breakers or \
           (datetime.utcnow() - self.circuit_breakers[component]['activated_at']).total_seconds() > self.circuit_breaker_timeout:
            
            self.circuit_breakers[component] = {
                'activated_at': datetime.utcnow(),
                'active': True
            }
            logger.warning(f"Circuit breaker activated for {component}")
    
    def is_circuit_breaker_active(self, component):
        """Check if circuit breaker is active for a component"""
        if component not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[component]
        
        # Check if timeout has passed
        if (datetime.utcnow() - breaker['activated_at']).total_seconds() > self.circuit_breaker_timeout:
            del self.circuit_breakers[component]
            # Reset error counts
            keys_to_remove = [k for k in self.error_counts.keys() if k.startswith(component)]
            for key in keys_to_remove:
                del self.error_counts[key]
            return False
        
        return breaker['active']
    
    def reset_circuit_breaker(self, component):
        """Manually reset circuit breaker for a component"""
        if component in self.circuit_breakers:
            del self.circuit_breakers[component]
            logger.info(f"Circuit breaker reset for {component}")
    
    def get_error_stats(self):
        """Get error statistics"""
        return {
            'error_counts': self.error_counts,
            'last_errors': self.last_errors,
            'active_circuit_breakers': {k: v for k, v in self.circuit_breakers.items() if v['active']}
        }


def retry_on_error(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Decorator for retrying functions on error with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {current_delay}s: {e}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator


def safe_execute(component_name, error_handler):
    """
    Decorator for safe execution with error handling
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler.record_error(component_name, e)
                
                # Check circuit breaker
                if error_handler.is_circuit_breaker_active(component_name):
                    logger.error(f"Circuit breaker active for {component_name}, skipping execution")
                    return None
                
                # Re-raise if it's a critical error
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                
                return None
        return wrapper
    return decorator


class HealthChecker:
    """Health checking for system components"""
    
    def __init__(self):
        self.component_health = {}
        self.last_check = {}
    
    def check_component(self, component_name, check_func):
        """Check health of a component"""
        try:
            is_healthy = check_func()
            self.component_health[component_name] = {
                'healthy': is_healthy,
                'last_check': datetime.utcnow(),
                'message': 'OK' if is_healthy else 'Unhealthy'
            }
            return is_healthy
        except Exception as e:
            self.component_health[component_name] = {
                'healthy': False,
                'last_check': datetime.utcnow(),
                'message': str(e)
            }
            return False
    
    def get_health_status(self):
        """Get overall health status"""
        healthy_count = sum(1 for v in self.component_health.values() if v['healthy'])
        total_count = len(self.component_health)
        
        return {
            'overall_healthy': healthy_count == total_count,
            'healthy_components': healthy_count,
            'total_components': total_count,
            'component_details': self.component_health
        }


class GracefulShutdown:
    """Handle graceful shutdown of the system"""
    
    def __init__(self):
        self.shutdown_hooks = []
        self.is_shutting_down = False
    
    def register_shutdown_hook(self, hook):
        """Register a function to call during shutdown"""
        self.shutdown_hooks.append(hook)
    
    async def shutdown(self):
        """Execute graceful shutdown"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        logger.info("Starting graceful shutdown...")
        
        # Execute shutdown hooks
        for hook in reversed(self.shutdown_hooks):
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                logger.error(f"Error during shutdown hook: {e}")
        
        logger.info("Graceful shutdown completed")


# Global error handler instance
global_error_handler = ErrorHandler()
global_health_checker = HealthChecker()
global_shutdown_handler = GracefulShutdown()