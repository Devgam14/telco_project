from auth.auth_service import Auth

def main():
    # 1. Initialize Auth
    authenticator = Auth()

    # 2. Authenticate the user (loops until login or exit)
    active_ui = authenticator.start()

    # 3. Launch the Dashboard
    # If it's AdminUI, it calls main_menu(). If UserUI, it calls user_menu().
    if hasattr(active_ui, 'main_menu'):
        active_ui.main_menu()
    else:
        active_ui.user_menu()

if __name__ == "__main__":
    main()