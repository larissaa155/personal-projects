import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { TaskService, Task } from '../task.service';
import { AuthService } from '../../../core/auth/auth.service';
import { Subject, takeUntil, debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.component.html',
  styleUrls: ['./task-list.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule]
})
export class TaskListComponent implements OnInit, OnDestroy {
  tasks: Task[] = [];
  filteredTasks: Task[] = [];
  isLoading = false;
  filterForm!: FormGroup;
  private destroy$ = new Subject<void>();

  statusColors = {
    todo: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    review: 'bg-purple-100 text-purple-800',
    done: 'bg-green-100 text-green-800'
  };

  priorityColors = {
    low: 'text-gray-600',
    medium: 'text-blue-600',
    high: 'text-orange-600',
    urgent: 'text-red-600'
  };

  constructor(
    private taskService: TaskService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {}

  ngOnInit(): void {
    this.initFilterForm();
    this.loadTasks();
    this.setupFilterSubscription();
  }

  initFilterForm(): void {
    this.filterForm = this.fb.group({
      search: [''],
      status: [''],
      priority: [''],
      assigned_to: ['']
    });
  }

  loadTasks(): void {
    this.isLoading = true;
    this.taskService.getTasks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tasks) => {
          this.tasks = tasks;
          this.applyFilters();
          this.isLoading = false;
        },
        error: () => {
          this.isLoading = false;
        }
      });
  }

  setupFilterSubscription(): void {
    this.filterForm.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        this.applyFilters();
      });
  }

  applyFilters(): void {
    const { search, status, priority, assigned_to } = this.filterForm.value;
    
    this.filteredTasks = this.tasks.filter(task => {
      let match = true;

      if (search) {
        const searchLower = search.toLowerCase();
        match = match && (
          task.title.toLowerCase().includes(searchLower) ||
          (task.description?.toLowerCase().includes(searchLower) || false)
        );
      }

      if (status) {
        match = match && task.status === status;
      }

      if (priority) {
        match = match && task.priority === priority;
      }

      if (assigned_to) {
        match = match && task.assigned_to_id === +assigned_to;
      }

      return match;
    });
  }

  getStatusClass(status: string): string {
    return this.statusColors[status as keyof typeof this.statusColors] || '';
  }

  getPriorityClass(priority: string): string {
    return this.priorityColors[priority as keyof typeof this.priorityColors] || '';
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  isOverdue(task: Task): boolean {
    return task.due_date ? new Date(task.due_date) < new Date() && task.status !== 'done' : false;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}