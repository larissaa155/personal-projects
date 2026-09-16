import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: Date;
  created_at: Date;
  updated_at: Date;
  completed_at?: Date;
  created_by_id: number;
  assigned_to_id?: number;
  team_id?: number;
  created_by?: any;
  assigned_to?: any;
}

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private apiUrl = `${environment.apiUrl}/tasks`;
  private tasksSubject = new BehaviorSubject<Task[]>([]);
  public tasks$ = this.tasksSubject.asObservable();

  constructor(private http: HttpClient) {}

  getTasks(params?: any): Observable<Task[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }

    return this.http.get<Task[]>(this.apiUrl, { params: httpParams })
      .pipe(
        tap(tasks => this.tasksSubject.next(tasks))
      );
  }

  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.apiUrl}/${id}`);
  }

  createTask(task: Partial<Task>): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, task)
      .pipe(
        tap(newTask => {
          const currentTasks = this.tasksSubject.value;
          this.tasksSubject.next([newTask, ...currentTasks]);
        })
      );
  }

  updateTask(id: number, task: Partial<Task>): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${id}`, task)
      .pipe(
        tap(updatedTask => {
          const currentTasks = this.tasksSubject.value;
          const index = currentTasks.findIndex(t => t.id === id);
          if (index !== -1) {
            currentTasks[index] = updatedTask;
            this.tasksSubject.next([...currentTasks]);
          }
        })
      );
  }

  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`)
      .pipe(
        tap(() => {
          const currentTasks = this.tasksSubject.value;
          this.tasksSubject.next(currentTasks.filter(t => t.id !== id));
        })
      );
  }

  assignTask(taskId: number, userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${taskId}/assign/${userId}`, {});
  }

  getTasksByStatus(status: string): Observable<Task[]> {
    return this.getTasks({ status });
  }

  getTasksByUser(userId: number): Observable<Task[]> {
    return this.getTasks({ assigned_to: userId });
  }
}