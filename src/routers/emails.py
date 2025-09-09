
@router.post("/", response_model=EmailResponse)
async def send_email(
    email: EmailCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_email = create_email(db, current_user.id, email.recipient_ids, email.subject, email.body)
    background_tasks.add_task(send_email_from_db, db, db_email.id)
    return db_email
