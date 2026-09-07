from app import create_app, db

app = create_app()


def main():
    with app.app_context():
        try:
            db.create_all()
        except Exception as err:
            print(f"[AVISO] No se pudo conectar a la base de datos configurada: {err}")
            print("[AVISO] Utilizando base de datos SQLite local alternativa (edi.db)...")
            from sqlalchemy import create_engine
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///edi.db"
            db.engine.dispose()
            db.engine = create_engine("sqlite:///edi.db")
            db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()