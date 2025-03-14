def validate_worker_input(worker_name, labor_hours, activity_code):
    errors = {}

    # Check if worker name is provided
    if not worker_name:
        errors['worker_name'] = 'Please select a worker.'

    # Check if labor hours is a number and within range
    try:
        hours = float(labor_hours)
        if hours <= 0 or hours > 24:
            errors['labor_hours'] = 'Enter valid hours (1-24).'
    except ValueError:
        errors['labor_hours'] = 'Enter a number for hours.'

    # Check if activity code is provided
    if not activity_code:
        errors['activity_code'] = 'Please select an activity code.'

    return errors
