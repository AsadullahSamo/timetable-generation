import unittest
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, time
from ..models import (
    ScheduleConfig, Subject, Teacher, Classroom, 
    TimetableEntry, ScheduleConfig
)
from ..algorithms.advanced_scheduler import AdvancedTimetableScheduler
from ..constraint_manager import ConstraintManager, ConstraintCategory
import json

class AdvancedSchedulerTestCase(TestCase):
    """Test cases for the advanced timetable scheduler"""
    
    def setUp(self):
        """Set up test data"""
        # Create test subjects
        self.math_subject = Subject.objects.create(
            name="Mathematics",
            code="MATH101",
            credits=3,
            is_practical=False
        )
        
        self.physics_subject = Subject.objects.create(
            name="Physics",
            code="PHYS101",
            credits=3,
            is_practical=True
        )
        
        self.chemistry_subject = Subject.objects.create(
            name="Chemistry",
            code="CHEM101",
            credits=2,
            is_practical=False
        )
        
        # Create test teachers
        self.teacher1 = Teacher.objects.create(
            name="Dr. Smith",
            email="smith@university.edu",
            max_lessons_per_day=4,
            unavailable_periods={}
        )
        self.teacher1.subjects.add(self.math_subject, self.physics_subject)
        
        self.teacher2 = Teacher.objects.create(
            name="Dr. Johnson",
            email="johnson@university.edu",
            max_lessons_per_day=5,
            unavailable_periods={}
        )
        self.teacher2.subjects.add(self.chemistry_subject)
        
        # Create test classrooms
        self.classroom1 = Classroom.objects.create(
            name="Room 101",
            capacity=30,
            building="Main Building"
        )
        
        self.lab1 = Classroom.objects.create(
            name="Physics Lab",
            capacity=20,
            building="Science Building"
        )
        
        # Create schedule configuration
        self.config = ScheduleConfig.objects.create(
            name="Test Schedule",
            days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            periods=["1", "2", "3", "4", "5", "6", "7", "8"],
            start_time=time(8, 0),
            lesson_duration=60,
            class_groups=["CS-1A", "CS-1B"],
            constraints=[]
        )
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        self.assertEqual(scheduler.population_size, 50)
        self.assertEqual(scheduler.generations, 100)
        self.assertEqual(scheduler.mutation_rate, 0.1)
        self.assertEqual(len(scheduler.subjects), 3)
        self.assertEqual(len(scheduler.teachers), 2)
        self.assertEqual(len(scheduler.classrooms), 2)
    
    def test_time_slot_creation(self):
        """Test time slot creation"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        self.assertEqual(len(scheduler.time_slots), 8)
        
        # Check first time slot
        first_slot = scheduler.time_slots[0]
        self.assertEqual(first_slot.start_time, time(8, 0))
        self.assertEqual(first_slot.end_time, time(9, 0))
    
    def test_random_solution_creation(self):
        """Test random solution creation"""
        scheduler = AdvancedTimetableScheduler(self.config)
        solution = scheduler._create_random_solution()
        
        self.assertIsNotNone(solution)
        self.assertIsInstance(solution.entries, list)
        self.assertGreater(len(solution.entries), 0)
    
    def test_practical_block_scheduling(self):
        """Test practical block scheduling"""
        scheduler = AdvancedTimetableScheduler(self.config)
        entries = []
        
        # Test scheduling a practical block
        success = scheduler._schedule_practical_block_random(
            entries, self.physics_subject, "CS-1A"
        )
        
        # Should find a 3-hour block for practical
        if success:
            practical_entries = [e for e in entries if e.is_practical]
            self.assertGreaterEqual(len(practical_entries), 3)
    
    def test_theory_subject_scheduling(self):
        """Test theory subject scheduling"""
        scheduler = AdvancedTimetableScheduler(self.config)
        entries = []
        
        # Test scheduling theory subjects
        scheduler._schedule_theory_subject_random(
            entries, self.math_subject, "CS-1A"
        )
        
        theory_entries = [e for e in entries if not e.is_practical]
        self.assertGreater(len(theory_entries), 0)
    
    def test_constraint_validation(self):
        """Test constraint validation"""
        constraint_manager = ConstraintManager(self.config)
        
        # Test validation
        is_valid = constraint_manager.validate_constraints()
        self.assertTrue(is_valid)
        
        # Test constraint summary
        summary = constraint_manager.get_constraint_summary()
        self.assertIn('total_constraints', summary)
        self.assertIn('active_constraints', summary)
    
    def test_teacher_availability_constraint(self):
        """Test teacher availability constraint"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Create a solution with teacher conflicts
        solution = scheduler._create_random_solution()
        
        # Test constraint checking
        penalty, violations = scheduler._check_teacher_availability(solution)
        
        # Should not have violations for valid data
        self.assertIsInstance(penalty, float)
        self.assertIsInstance(violations, list)
    
    def test_room_type_compatibility(self):
        """Test room type compatibility"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Test practical subject with lab
        is_compatible = scheduler._is_room_compatible(self.lab1, self.physics_subject)
        self.assertTrue(is_compatible)
        
        # Test practical subject with regular classroom
        is_compatible = scheduler._is_room_compatible(self.classroom1, self.physics_subject)
        self.assertFalse(is_compatible)
    
    def test_subject_frequency_constraint(self):
        """Test subject frequency constraint"""
        scheduler = AdvancedTimetableScheduler(self.config)
        solution = scheduler._create_random_solution()
        
        penalty, violations = scheduler._check_subject_frequency(solution)
        
        self.assertIsInstance(penalty, float)
        self.assertIsInstance(violations, list)
    
    def test_practical_blocks_constraint(self):
        """Test practical blocks constraint"""
        scheduler = AdvancedTimetableScheduler(self.config)
        solution = scheduler._create_random_solution()
        
        penalty, violations = scheduler._check_practical_blocks(solution)
        
        self.assertIsInstance(penalty, float)
        self.assertIsInstance(violations, list)
    
    def test_genetic_algorithm_evolution(self):
        """Test genetic algorithm evolution"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Test population initialization
        population = scheduler._initialize_population()
        self.assertEqual(len(population), scheduler.population_size)
        
        # Test tournament selection
        selected = scheduler._tournament_selection(population)
        self.assertIn(selected, population)
        
        # Test crossover
        parent1 = population[0]
        parent2 = population[1]
        child = scheduler._crossover(parent1, parent2)
        self.assertIsInstance(child.entries, list)
        
        # Test mutation
        mutated = scheduler._mutate(child)
        self.assertIsInstance(mutated.entries, list)
    
    def test_solution_evaluation(self):
        """Test solution evaluation"""
        scheduler = AdvancedTimetableScheduler(self.config)
        solution = scheduler._create_random_solution()
        
        fitness, violations = scheduler._evaluate_solution(solution)
        
        self.assertIsInstance(fitness, float)
        self.assertIsInstance(violations, list)
        self.assertGreater(fitness, 0)  # Should have positive fitness
    
    def test_complete_generation(self):
        """Test complete timetable generation"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Reduce parameters for faster testing
        scheduler.population_size = 10
        scheduler.generations = 5
        
        result = scheduler.generate_timetable()
        
        self.assertIn('success', result)
        self.assertIn('entries', result)
        self.assertIn('fitness_score', result)
        self.assertIn('constraint_violations', result)
    
    def test_large_dataset_performance(self):
        """Test performance with larger datasets"""
        # Create more test data
        for i in range(10):
            Subject.objects.create(
                name=f"Subject {i}",
                code=f"SUB{i:03d}",
                credits=2 + (i % 3),
                is_practical=(i % 2 == 0)
            )
        
        for i in range(5):
            Teacher.objects.create(
                name=f"Teacher {i}",
                email=f"teacher{i}@university.edu",
                max_lessons_per_day=4
            )
        
        for i in range(8):
            Classroom.objects.create(
                name=f"Room {i}",
                capacity=25 + (i * 5),
                building="Main Building"
            )
        
        # Update config with more class groups
        self.config.class_groups = [f"CS-{i}A" for i in range(1, 6)]
        self.config.save()
        
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Test with reduced parameters for performance
        scheduler.population_size = 20
        scheduler.generations = 10
        
        import time
        start_time = time.time()
        
        result = scheduler.generate_timetable()
        
        generation_time = time.time() - start_time
        
        self.assertLess(generation_time, 30)  # Should complete within 30 seconds
        self.assertIn('success', result)
    
    def test_constraint_conflicts(self):
        """Test constraint conflict detection"""
        constraint_manager = ConstraintManager(self.config)
        
        # Add conflicting constraints
        conflicting_constraints = [
            {
                'id': 'block_constraint',
                'name': 'Practical Blocks',
                'category': 'time',
                'parameters': {'type': 'block', 'duration_hours': 3},
                'weight': 8.0,
                'is_hard': True
            },
            {
                'id': 'break_constraint',
                'name': 'Break Time',
                'category': 'time',
                'parameters': {'type': 'break', 'min_break_minutes': 15},
                'weight': 4.0,
                'is_hard': False
            }
        ]
        
        # Test conflict detection
        self.config.constraints = conflicting_constraints
        self.config.save()
        
        constraint_manager = ConstraintManager(self.config)
        is_valid = constraint_manager.validate_constraints()
        
        # Should detect conflicts
        self.assertFalse(is_valid)
        self.assertGreater(len(constraint_manager.validation_errors), 0)
    
    def test_optimization_parameters(self):
        """Test different optimization parameters"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Test different parameter sets
        parameter_sets = [
            {'population_size': 20, 'generations': 10, 'mutation_rate': 0.15},
            {'population_size': 30, 'generations': 15, 'mutation_rate': 0.1},
            {'population_size': 40, 'generations': 20, 'mutation_rate': 0.05}
        ]
        
        results = []
        
        for params in parameter_sets:
            scheduler.population_size = params['population_size']
            scheduler.generations = params['generations']
            scheduler.mutation_rate = params['mutation_rate']
            
            result = scheduler.generate_timetable()
            results.append({
                'params': params,
                'fitness': result.get('fitness_score', 0),
                'time': result.get('generation_time', 0)
            })
        
        # All should complete successfully
        for result in results:
            self.assertGreater(result['fitness'], 0)
            self.assertGreater(result['time'], 0)
    
    def test_error_handling(self):
        """Test error handling in scheduler"""
        scheduler = AdvancedTimetableScheduler(self.config)
        
        # Test with invalid data
        with self.assertRaises(Exception):
            # This should raise an exception for invalid operations
            scheduler._get_time_slot("InvalidDay", 999)
    
    def test_memory_efficiency(self):
        """Test memory efficiency of the scheduler"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        scheduler = AdvancedTimetableScheduler(self.config)
        scheduler.population_size = 50
        scheduler.generations = 10
        
        result = scheduler.generate_timetable()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
    
    def test_concurrent_generation(self):
        """Test concurrent timetable generation"""
        import threading
        import time
        
        results = []
        errors = []
        
        def generate_timetable():
            try:
                scheduler = AdvancedTimetableScheduler(self.config)
                scheduler.population_size = 10
                scheduler.generations = 5
                result = scheduler.generate_timetable()
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=generate_timetable)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All should complete successfully
        self.assertEqual(len(results), 3)
        self.assertEqual(len(errors), 0)
        
        # All results should be valid
        for result in results:
            self.assertIn('success', result)
            self.assertIn('fitness_score', result)

if __name__ == '__main__':
    unittest.main() 