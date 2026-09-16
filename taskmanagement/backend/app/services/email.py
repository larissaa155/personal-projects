import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from fastapi import BackgroundTasks
from app.core.config import settings

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    background_tasks: Optional[BackgroundTasks] = None
):
    """
    Send email using SMTP
    """
    if not settings.SMTP_HOST:
        print(f"Email would be sent to {to_email}: {subject}")
        return
    
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

async def send_welcome_email(to_email: str, username: str):
    """Send welcome email to new users"""
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to TaskFlow! 🎉</h2>
            <p>Hi <strong>{username}</strong>,</p>
            <p>Welcome to TaskFlow - your modern task management system!</p>
            <p>Here's what you can do:</p>
            <ul>
                <li>Create and manage tasks</li>
                <li>Collaborate with team members</li>
                <li>Track your productivity</li>
                <li>Set priorities and deadlines</li>
            </ul>
            <p>Get started by creating your first task!</p>
            <br>
            <p>Best regards,<br>The TaskFlow Team</p>
        </body>
    </html>
    """
    await send_email(to_email, "Welcome to TaskFlow!", html_content)

async def send_task_assignment_email(
    to_email: str,
    task_title: str,
    assigned_by: str,
    due_date: Optional[str] = None
):
    """Send email when a task is assigned"""
    due_date_text = f"<p><strong>Due Date:</strong> {due_date}</p>" if due_date else ""
    
    html_content = f"""
    <html>
        <body>
            <h2>New Task Assigned 📋</h2>
            <p>Hi,</p>
            <p>You have been assigned a new task: <strong>{task_title}</strong></p>
            <p><strong>Assigned by:</strong> {assigned_by}</p>
            {due_date_text}
            <p>Please log in to TaskFlow to view and manage this task.</p>
            <br>
            <p>Best regards,<br>The TaskFlow Team</p>
        </body>
    </html>
    """
    await send_email(to_email, f"New Task Assigned: {task_title}", html_content)

async def send_task_completed_email(
    to_email: str,
    task_title: str,
    completed_by: str
):
    """Send email when a task is completed"""
    html_content = f"""
    <html>
        <body>
            <h2>Task Completed ✅</h2>
            <p>Hi,</p>
            <p>The task <strong>{task_title}</strong> has been marked as complete.</p>
            <p><strong>Completed by:</strong> {completed_by}</p>
            <p>You can review the completed task in TaskFlow.</p>
            <br>
            <p>Best regards,<br>The TaskFlow Team</p>
        </body>
    </html>
    """
    await send_email(to_email, f"Task Completed: {task_title}", html_content)

async def send_task_overdue_email(
    to_email: str,
    task_title: str,
    due_date: str
):
    """Send email when a task is overdue"""
    html_content = f"""
    <html>
        <body>
            <h2>Task Overdue ⚠️</h2>
            <p>Hi,</p>
            <p>The task <strong>{task_title}</strong> is now overdue.</p>
            <p><strong>Due Date:</strong> {due_date}</p>
            <p>Please update the task status or extend the due date.</p>
            <br>
            <p>Best regards,<br>The TaskFlow Team</p>
        </body>
    </html>
    """
    await send_email(to_email, f"Task Overdue: {task_title}", html_content)

async def send_password_reset_email(to_email: str, username: str, reset_token: str):
    """Send password reset email"""
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Password Reset Request 🔑</h2>
            <p>Hi <strong>{username}</strong>,</p>
            <p>We received a request to reset your password.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The TaskFlow Team</p>
        </body>
    </html>
    """
    await send_email(to_email, "Password Reset Request", html_content)