import os

base = r"C:\Users\ADMIN\Documents\EDI PROJECT\aegis"
dirs = [
    r"apps\api\app\api\v1",
    r"apps\api\app\core",
    r"apps\api\app\db",
    r"apps\api\app\models",
    r"apps\api\app\schemas",
    r"apps\api\app\services",
    r"apps\api\app\worker",
    r"apps\api\alembic\versions",
    r"apps\web\src\app\(dashboard)\dashboard",
    r"apps\web\src\app\(dashboard)\alerts\[alertId]",
    r"apps\web\src\app\(dashboard)\accounts\[accountId]",
    r"apps\web\src\app\(dashboard)\transactions",
    r"apps\web\src\app\(dashboard)\cases",
    r"apps\web\src\app\(dashboard)\graph",
    r"apps\web\src\app\(dashboard)\data-import",
    r"apps\web\src\app\auth\login",
    r"apps\web\src\app\auth\register",
    r"apps\web\src\components\layout",
    r"apps\web\src\components\ui",
    r"apps\web\src\lib",
    r"apps\web\src\store",
    r"ml\temporal",
    r"ml\behavioral",
    r"ml\graph",
    r"ml\fusion",
    r"ml\verification",
    r"ml\explainability",
    r"ml\llm",
    r"data\sample",
    r"docker\api",
    r"docker\web",
    r"docker\nginx",
    r"docker\postgres",
    r"tests",
    r"scripts",
]

for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)

print("ALL_DIRS_CREATED")
