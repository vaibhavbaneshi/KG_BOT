def safe_run(func, *args, **kwargs):
    """
    Run a function safely with error handling.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"