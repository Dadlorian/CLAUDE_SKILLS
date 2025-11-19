"""Intelligent payment routing"""
import logging

class PaymentRouter:
    def __init__(self, processor_metrics):
        self.metrics = processor_metrics
        self.logger = logging.getLogger(__name__)

    def select(self, request):
        """Select best processor for transaction"""
        # Get eligible processors
        eligible = self._get_eligible_processors(request)
        
        # Score each processor
        scores = {}
        for proc_name in eligible:
            score = self._score_processor(proc_name, request)
            scores[proc_name] = score
        
        best = max(scores.items(), key=lambda x: x[1])[0]
        self.logger.debug(f"Selected {best} for {request}")
        return best

    def get_fallback_chain(self, primary):
        """Get fallback chain for processor"""
        chain = [primary]
        # Add alternates by success rate
        all_procs = sorted(
            self.metrics.processors,
            key=lambda p: self.metrics.get_success_rate(p),
            reverse=True
        )
        chain.extend([p for p in all_procs if p != primary][:3])
        return chain

    def _get_eligible_processors(self, request):
        # Filter by capability
        return ['stripe', 'adyen', 'square']

    def _score_processor(self, proc_name, request):
        success_rate = self.metrics.get_success_rate(proc_name)
        cost = self.metrics.get_cost(proc_name)
        latency = self.metrics.get_latency(proc_name)
        
        return success_rate * 0.4 - (cost * 0.3) - (latency * 0.3)
