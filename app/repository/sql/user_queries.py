from sqlalchemy import text

SELECT_USER = text(
    """
    select user_id, login, name, surname as last_name, phone, role_id from "user" where login = :user
    """
)

SELECT_USER_CREDS = text(
    """
    select user_id, login, password, name, surname as last_name, phone, role_id from "user" where login = :user
    """
)

CREATE_USER = text(
    """
    INSERT INTO "user" (login, password, name, surname, phone, role_id)
    values (:login, :password, :name, :surname, :phone, :role_id)
    on conflict(login) do nothing
    returning *
    """
)
