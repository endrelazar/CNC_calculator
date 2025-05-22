import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from app import MegmunkalasAdat
from werkzeug.security import generate_password_hash
from unittest.mock import patch

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Teszt adatbázis memóriában
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "teszt-titkos-kulcs"
    global users
    users = {"admin": generate_password_hash("admin")}

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_login_logout_flow(client):
    """Teszt a teljes bejelentkezés-kijelentkezés folyamatra"""
    
    # 1. Alap oldalbetöltés
    response = client.get("/login")
    assert response.status_code == 200
    assert b'<form method="POST"' in response.data
    
    # 2. Hibás bejelentkezési kísérlet
    response = client.post("/login", data={
        "username": "admin",
        "password": "rossz_jelszo"
    }, follow_redirects=True)
    assert b"Hib" in response.data  # "Hibás felhasználónév vagy jelszó"
    
    # Ellenőrizzük, hogy nincs bejelentkezve
    with client.session_transaction() as sess:
        assert 'user' not in sess
    
    # 3. Helyes bejelentkezés
    response = client.post("/login", data={
        "username": "admin",
        "password": "admin"
    }, follow_redirects=True)
    assert b"Sikeres bejelentkez" in response.data
    
    # Ellenőrizzük a session-t
    with client.session_transaction() as sess:
        assert 'user' in sess
        assert sess['user'] == 'admin'
    
    # 4. Védett oldal elérése bejelentkezés után
    response = client.get("/export")
    assert response.status_code == 200  # már nem irányít át

    # 5. Kijelentkezés
    response = client.get("/logout", follow_redirects=True)
    assert b"Sikeresen kijelentkezt" in response.data
    
    # Ellenőrizzük, hogy a kijelentkezés törölte a session-t
    with client.session_transaction() as sess:
        assert 'user' not in sess
    
    # 6. Védett oldal újra nem elérhető
    response = client.get("/export")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]



def test_adding_data_to_db(client):
    with app.app_context():
        db.session.query(MegmunkalasAdat).delete()  # törli az összes rekordot
        db.session.commit()
        # Új adat létrehozása
        new_data = MegmunkalasAdat(atmero=10, vc_inp=100, elotolas=0.2, 
                                    fogsz=4, fordulat=3183, eredmeny2_f=2546)
        db.session.add(new_data)
        db.session.commit()
        
        # Ellenőrizzük, hogy bekerült az adatbázisba
        saved = MegmunkalasAdat.query.filter_by(atmero=10, vc_inp=100).first()
        assert saved is not None
        assert saved.vc_inp == 100
        assert saved.eredmeny2_f == 2546

def test_deleting_data_from_db(client):
    with app.app_context():
        # Adat létrehozása, majd törlése
        new_data = MegmunkalasAdat(atmero=15, vc_inp=120, elotolas=0.3, 
                                    fogsz=2, fordulat=2546, eredmeny2_f=1527)
        db.session.add(new_data)
        db.session.commit()
        
        data_id = new_data.id
        db.session.delete(new_data)
        db.session.commit()
        
        # Ellenőrizzük, hogy tényleg törlődött
        assert db.session.get(MegmunkalasAdat, data_id) is None

def test_protected_routes_without_login(client):
    """Nem bejelentkezett felhasználók ne férhessenek hozzá védett oldalakhoz"""
    get_routes = ["/export", "/export_pdf"]
    post_routes = ["/szuro_torlese", "/kuldes"]
    
    
    for route in get_routes:
        response = client.get(route)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]
        
    # POST kérések tesztelése
    for route in post_routes:
        response = client.post(route)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

def test_megmunkalas_endpoint_error_handling(client):
    """Teszteli a hibakezelést a számítási végpontoknál"""
    # Érvénytelen adatokkal POST
    response = client.post("/megmunkalas", data={
        "muvelet": "1",
        "atmero_1": "nem szám",  # Hiba kell legyen
        "fordulat_1": "1000"
    }, follow_redirects=True)
    
    assert "Tölts ki minden mezőt!!!" in response.data.decode('utf-8')  

def test_filtering_adatok(client):
    with app.app_context():
        # Adatbázis törlése és újra létrehozása
        db.session.query(MegmunkalasAdat).delete()
        db.session.commit()
        # Teszt adatok létrehozása
        db.session.add(MegmunkalasAdat(atmero=10, vc_inp=100, elotolas=0.2, fogsz=4, fordulat=3183, eredmeny2_f=2546))
        db.session.add(MegmunkalasAdat(atmero=20, vc_inp=150, elotolas=0.3, fogsz=3, fordulat=2387, eredmeny2_f=2148))
        db.session.commit()
        
        # Szűrés tesztelése
        response = client.get("/eredmenyek?oszlop=atmero&feltetel=lt&ertek=15")
        content = response.data.decode('utf-8')
        
        # A 10mm átmérőjű adat megjelenik
        assert "<td>10" in content
        # A 20mm átmérőjű nem jelenik meg
        assert "<td>20</td>" not in content and "<td>20 </td>" not in content



def test_email_sending(client):
    with patch('app.kuld_email') as mock_send:
        # Bejelentkezés
        client.get('/')
        with client.session_transaction() as sess:
            sess['user'] = 'admin'
            
        # Adatok létrehozása az adatbázisban
        with app.app_context():
            db.session.add(MegmunkalasAdat(atmero=10, vc_inp=100, elotolas=0.2, 
                                          fogsz=4, fordulat=3183, eredmeny2_f=2546))
            db.session.commit()
        
        # E-mail küldési kérés
        response = client.post("/kuldes", data={
            "email": "teszt@example.com",
            "formatum": "csv"
        }, follow_redirects=True)
        
        # Ellenőrizzük, hogy meghívták az e-mail küldő függvényt
        mock_send.assert_called_once()
        assert b"elk" in response.data
        assert mock_send.call_args[0][0] == "teszt@example.com"
        assert mock_send.call_args[0][3] == "text/csv"

def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "CNC Számítási Központ".encode("utf-8") in response.data

