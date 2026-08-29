from database import db, cur


def methods():

    cur.execute("""
        SELECT *
        FROM payment_methods
        WHERE status=1
        ORDER BY id
    """)

    return cur.fetchall()


def method(mid):

    cur.execute(
        """
        SELECT *
        FROM payment_methods
        WHERE id=?
        """,
        (mid,)
    )

    return cur.fetchone()


def trx_exists(trx):

    cur.execute(
        """
        SELECT id
        FROM payments
        WHERE trxid=?
        """,
        (trx,)
    )

    return cur.fetchone() is not None


def create_payment(
    user,
    method,
    amount,
    trxid,
    screenshot
):

    cur.execute(
        """
        INSERT INTO payments(
            user,
            method,
            amount,
            trxid,
            screenshot,
            status
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            user,
            method,
            amount,
            trxid,
            screenshot,
            "pending"
        )
    )

    db.commit()

    return cur.lastrowid


def pending():

    cur.execute("""
        SELECT *
        FROM payments
        WHERE status='pending'
        ORDER BY id DESC
    """)

    return cur.fetchall()


def payment(pid):

    cur.execute(
        """
        SELECT *
        FROM payments
        WHERE id=?
        """,
        (pid,)
    )

    return cur.fetchone()


def approve(pid):

    cur.execute(
        "UPDATE payments SET status='approved' WHERE id=?",
        (pid,)
    )

    db.commit()


def reject(pid):

    cur.execute(
        "UPDATE payments SET status='rejected' WHERE id=?",
        (pid,)
    )

    db.commit()


def add_balance(user_id, amount):

    cur.execute(
        """
        UPDATE users
        SET balance = balance + ?
        WHERE id=?
        """,
        (amount, user_id)
    )

    db.commit()

def pending_payment(user):

    cur.execute(

        """
        SELECT id
        FROM payments
        WHERE user=?
        AND status='pending'
        """,

        (user,)

    )

    return cur.fetchone()

def add_method(name, number):

    cur.execute(
        """
        INSERT INTO payment_methods(
            name,
            number,
            status
        )
        VALUES(?,?,1)
        """,
        (
            name,
            number
        )
    )

    db.commit()

    return cur.lastrowid

def all_methods():

    cur.execute("""
        SELECT *
        FROM payment_methods
        ORDER BY id
    """)

    return cur.fetchall()

def method_by_id(mid):

    cur.execute(
        """
        SELECT *
        FROM payment_methods
        WHERE id=?
        """,
        (mid,)
    )

    return cur.fetchone()


def delete_method(mid):

    cur.execute(
        "DELETE FROM payment_methods WHERE id=?",
        (mid,)
    )

    db.commit()


def set_method_status(mid, status):

    cur.execute(
        """
        UPDATE payment_methods
        SET status=?
        WHERE id=?
        """,
        (
            status,
            mid
        )
    )

    db.commit()

def update_method_name(mid, name):

    cur.execute(
        """
        UPDATE payment_methods
        SET name=?
        WHERE id=?
        """,
        (
            name,
            mid
        )
    )

    db.commit()


def update_method_number(mid, number):

    cur.execute(
        """
        UPDATE payment_methods
        SET number=?
        WHERE id=?
        """,
        (
            number,
            mid
        )
    )

    db.commit()
