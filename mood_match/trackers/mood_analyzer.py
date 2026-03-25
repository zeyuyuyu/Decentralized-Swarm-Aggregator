import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class MoodAnalyzer:
    def __init__(self):
        self.mood_scale = {
            'very_happy': 5,
            'happy': 4, 
            'neutral': 3,
            'sad': 2,
            'very_sad': 1
        }
        
    def analyze_mood_patterns(self, mood_history: List[Dict]) -> Dict:
        """
        Analyzes mood patterns over time to detect trends and provide insights
        
        Args:
            mood_history: List of mood entries with 'mood' and 'timestamp' keys
            
        Returns:
            Dictionary containing mood analysis metrics and insights
        """
        if not mood_history:
            return {
                'average_mood': None,
                'mood_trend': None,
                'pattern_detected': None,
                'recommendations': []
            }

        # Convert moods to numerical values
        mood_values = [self.mood_scale[entry['mood']] for entry in mood_history]
        timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in mood_history]

        # Calculate basic metrics
        average_mood = np.mean(mood_values)
        
        # Detect trend (improving, declining, stable)
        trend = self._calculate_trend(mood_values)
        
        # Detect patterns
        pattern = self._detect_patterns(mood_values, timestamps)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(trend, pattern, average_mood)

        return {
            'average_mood': round(average_mood, 2),
            'mood_trend': trend,
            'pattern_detected': pattern,
            'recommendations': recommendations
        }

    def _calculate_trend(self, mood_values: List[float]) -> str:
        """Determines if mood is improving, declining, or stable"""
        if len(mood_values) < 2:
            return 'insufficient_data'
            
        slope = np.polyfit(range(len(mood_values)), mood_values, 1)[0]
        
        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        return 'stable'

    def _detect_patterns(self, mood_values: List[float], timestamps: List[datetime]) -> Optional[str]:
        """Detects common mood patterns"""
        if len(mood_values) < 5:
            return None

        # Check for weekly patterns
        weekly_averages = {}
        for mood, time in zip(mood_values, timestamps):
            day = time.strftime('%A')
            if day not in weekly_averages:
                weekly_averages[day] = []
            weekly_averages[day].append(mood)

        day_averages = {day: np.mean(moods) for day, moods in weekly_averages.items()}
        
        # Detect significant variations
        mean_mood = np.mean(list(day_averages.values()))
        std_mood = np.std(list(day_averages.values()))
        
        for day, avg in day_averages.items():
            if abs(avg - mean_mood) > std_mood:
                return f'weekly_pattern_{day}'
                
        # Check for mood swings
        differences = np.diff(mood_values)
        if np.std(differences) > 1.5:
            return 'mood_swings'
            
        return 'consistent'

    def _generate_recommendations(self, trend: str, pattern: Optional[str], average_mood: float) -> List[str]:
        """Generates personalized recommendations based on mood analysis"""
        recommendations = []
        
        if trend == 'declining':
            recommendations.append('Consider talking to a friend or professional about your feelings')
            recommendations.append('Try incorporating more physical activity into your routine')
            
        if pattern == 'mood_swings':
            recommendations.append('Track your sleep patterns and maintain a regular sleep schedule')
            recommendations.append('Practice mindfulness or meditation to stabilize mood')
            
        if average_mood < 2.5:
            recommendations.append('Focus on self-care activities that bring you joy')
            recommendations.append('Set small, achievable goals for each day')
            
        if pattern and pattern.startswith('weekly_pattern'):
            day = pattern.split('_')[-1]
            recommendations.append(f'Your mood tends to change on {day}s. Plan engaging activities for this day')
            
        return recommendations if recommendations else ['Keep tracking your mood to receive personalized insights']