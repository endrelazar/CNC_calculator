from flask import Flask, render_template, request, redirect, flash, session, url_for
from CNC_szamolo import szamitasok
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask import Response
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from CNC_szamolo.email_kuldo import kuld_email
import logging

#from werkzeug.security import generate_password_hash # Testing

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="arertesito.log",
    filemode="a"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

#users = {"admin": generate_password_hash("admin")}  #Testing
load_dotenv("ini.env")  
users = {"admin": os.getenv("USERPASS") }

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "..", "adatok.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = os.getenv("SECRET_KEY")

class MegmunkalasAdat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    atmero = db.Column(db.Float, nullable=False)
    vc_inp = db.Column(db.Float, nullable=False)
    elotolas = db.Column(db.Float, nullable=False)
    fogsz = db.Column(db.Float, nullable=False)
    fordulat = db.Column(db.Float, nullable=False)
    eredmeny2_f = db.Column(db.Float, nullable=False)
    datum = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            logging.info(f"Bejelentkezett: {username}")
            flash("Sikeres bejelentkezés!", "success")
            return redirect("/")
        else:
            logging.warning(f"Sikertelen bejelentkezési kísérlet: {username}")
            flash("Hibás felhasználónév vagy jelszó!", "danger")


    return render_template("login.html")

@app.route("/logout")
def logout():
    user = session.get('user')
    session.pop('user', None)
    logging.info(f"Kijelentkezett: {user}")  
    flash("Sikeresen kijelentkeztél.", "info")
    return redirect("/")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sullyesztes", methods=["GET", "POST"])
def sullyesztes():

    eredmeny = None
    hiba = None
    muvelet = ""

    if request.method == "POST":
        muvelet = request.form.get("muvelet")

        if muvelet == "1":
            try:
                szog_sz = float(request.form.get("szog_1", "").strip())
                melyseg = float(request.form.get("melyseg", "").strip())
                
                eredmeny = szamitasok.atmero_melysegen(float(szog_sz), float(melyseg))
            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"      
                   

        elif muvelet == "2":
            try:
                szog_sz = float(request.form.get("szog_2", "").strip())
                atmero = float(request.form.get("atmero", "").strip())
                
                eredmeny = szamitasok.melyseg_valtozas(float(szog_sz), float(atmero))

            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"

        elif muvelet == "3":
            try:
                szog_sz = float(request.form.get("szog_3", "").strip())
                m_melyseg = float(request.form.get("m_melyseg", "").strip())
                r_melyseg = float(request.form.get("r_melyseg", "").strip())

                eredmeny1 = szamitasok.atmero_melysegen(float(szog_sz), float(r_melyseg))
                eredmeny2 = szamitasok.atmero_melysegen(float(szog_sz), float(m_melyseg))
                sugar_diff = (eredmeny2 - eredmeny1) / 2
                eredmeny = szamitasok.melyseg_sugarbol(float(szog_sz), sugar_diff)
            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"

        elif muvelet == "4":
            try:
                szog_sz = float(request.form.get("szog_4", "").strip())
                mert = float(request.form.get("mert_atmero", "").strip())
                rajzi = float(request.form.get("rajzi_atmero", "").strip())

                eredmeny = szamitasok.melyseg_valtozas(float(szog_sz), float(mert)) - szamitasok.melyseg_valtozas(float(szog_sz), float(rajzi))
            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"  

        elif muvelet == "5":
            try:
                szog_sz = float(request.form.get("szog_5", "").strip())
                furat = float(request.form.get("furat", "").strip())
                sullyn = float(request.form.get("sullyn", "").strip())

                eredmeny = szamitasok.melyseg_valtozas(float(szog_sz), float(sullyn)) - szamitasok.melyseg_valtozas(float(szog_sz), float(furat))
                
            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"

    return render_template("sullyesztes.html", eredmeny=eredmeny, hiba=hiba, muvelet=muvelet)




@app.route("/megmunkalas", methods=["GET", "POST"])
def megmunkalas():
    eredmeny1 = None
    eredmeny2 = None
    eredmeny3 = None
    hiba = None
    muvelet = ""

    if request.method == "POST":
        muvelet = request.form.get("muvelet")

        if muvelet == "1":

            try: 
                atmero = float(request.form.get("atmero_1", "").strip())
                fordulat = float(request.form.get("fordulat_1", "").strip())
                
                eredmeny1 = szamitasok.forgacsolo_sebesseg(float(atmero), float(fordulat))
            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")    
                hiba = "Tölts ki minden mezőt!!!"

        elif muvelet == "2":
            try:
                atmero = float(request.form.get("atmero_2", "").strip())
                vc_inp = float(request.form.get("vagosebinput", "").strip())
                elotolas = float(request.form.get("elotolas", "").strip())
                fogsz = float(request.form.get("fogszam", "").strip())
                
                fordulat = szamitasok.szeradatbol_fordulat(float(vc_inp), float(atmero))
                eredmeny2_s = fordulat
                eredmeny2_f = szamitasok.elotolasi_sebesseg_maro(float(eredmeny2_s), float(elotolas), float(fogsz))
                eredmeny2 = f"Fordulat S = {fordulat:.0f} RPM , Előtolás F = {eredmeny2_f:.0f} mm/p" 

                uj_adat = MegmunkalasAdat(atmero=atmero,vc_inp=vc_inp,elotolas=elotolas,fogsz=fogsz,fordulat=fordulat,eredmeny2_f=eredmeny2_f)

                db.session.add(uj_adat)
                db.session.commit()


            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"  
                


        elif muvelet == "3":
            try:
                fordulat = float(request.form.get("fordulat_3", "").strip())
                menetem = float(request.form.get("menetem", "").strip())
                eredmeny3 = float(szamitasok.menet_parameter(float(fordulat),float(menetem)))
                
            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"      


        

       
    return render_template("megmunkalas.html", eredmeny1=eredmeny1,eredmeny2=eredmeny2,eredmeny3=eredmeny3, hiba=hiba, muvelet=muvelet)

@app.route("/nullpontforgatas", methods=["GET", "POST"])
def nullpontforgatas():
    eredmeny = None
    hiba = None
    gep_tipus = ""

    if request.method == "POST":
        gep_tipus = request.form.get("gep_tipus", "")

        if gep_tipus == "fuggoleges":
            try:
                gY = float(request.form.get("gép_y", "").strip())
                gZ = float(request.form.get("gép_z_f", "").strip())
                mY = float(request.form.get("mkd_y", "").strip())
                mZ = float(request.form.get("mkd_z_f", "").strip())
                szamitasok = float(request.form.get("szog_f", "").strip())

                machine_zero = np.array([0, gY, gZ])
                workpiece_zero = np.array([0, mY, mZ])
                angle_rad = np.radians(szamitasok)

                rotation_matrix = np.array([
                    [1, 0, 0],
                    [0, np.cos(angle_rad), -np.sin(angle_rad)],
                    [0, np.sin(angle_rad),  np.cos(angle_rad)]])

                relative_vector = workpiece_zero - machine_zero
                rotated_vector = rotation_matrix @ relative_vector
                new_zero = machine_zero + rotated_vector

                eredmeny = f"X: 0, Y: {new_zero[1]:.2f}, Z: {new_zero[2]:.2f}"

            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"
   

        elif gep_tipus == "vizszintes":
            try:
                gX = float(request.form.get("gép_x", "").strip())
                gZ = float(request.form.get("gép_z_v", "").strip())
                mX = float(request.form.get("mkd_x", "").strip())
                mZ = float(request.form.get("mkd_z_v", "").strip())
                szamitasok = float(request.form.get("szog_v", "").strip())
                
                machine_zero = np.array([gX, 0, gZ])
                workpiece_zero = np.array([mX, 0, mZ])
                angle_rad = np.radians(szamitasok)

                rotation_matrix = np.array([
                [ np.cos(angle_rad), 0, np.sin(angle_rad)],
                [ 0,                1, 0],
                [-np.sin(angle_rad), 0, np.cos(angle_rad)]])

                relative_vector = machine_zero - workpiece_zero
                rotated_vector = rotation_matrix @ relative_vector
                new_zero = machine_zero + rotated_vector

                eredmeny = f"X: {new_zero[0]:.2f}, Y: 0, Z: {new_zero[2]:.2f}"

            except ValueError:
                logging.error("Hiba a bemeneti adatok konvertálásakor.")
                hiba = "Tölts ki minden mezőt!!!"

        else:
            logging.error("Hiba a gép típusának kiválasztásakor.")
            hiba = "Válassz géptípust!"


    return render_template("nullpontforgatas.html", eredmeny=eredmeny, hiba=hiba, gep_tipus=gep_tipus)


@app.route("/eredmenyek")
def eredmenyek():
    oszlop = request.args.get("oszlop")
    feltetel = request.args.get("feltetel")
    ertek = request.args.get("ertek")
    # Szűrés mentése session-be
    if oszlop and feltetel and ertek:
        session['szures'] = {'oszlop': oszlop, 'feltetel': feltetel, 'ertek': ertek}
    elif 'szures' in session:
        oszlop = session['szures'].get('oszlop')
        feltetel = session['szures'].get('feltetel')
        ertek = session['szures'].get('ertek')

    query = MegmunkalasAdat.query

    if oszlop and feltetel and ertek:
        try:
            column = getattr(MegmunkalasAdat, oszlop)
            value = float(ertek)
            if feltetel == "eq":
                query = query.filter(column == value)
            elif feltetel == "lt":
                query = query.filter(column < value)
            elif feltetel == "gt":
                query = query.filter(column > value)
            elif feltetel == "le":
                query = query.filter(column <= value)
            elif feltetel == "ge":
                query = query.filter(column >= value)
        except Exception:
            logging.error(f"Hibás szűrési feltétel: {oszlop}, {feltetel}, {ertek}")
            flash("Hibás szűrési feltétel!", "danger")

    adatok = query.order_by(MegmunkalasAdat.datum.desc()).all()
    return render_template("eredmenyek.html", adatok=adatok)

@app.route("/kuldes", methods=["POST"])
def manualis_kuldes():
    if 'user' not in session:
        return redirect("/login")
    
    email = request.form.get("email")
    formatum = request.form.get("formatum", "csv")

        # Szűrés session-ből
    oszlop = session.get('szures', {}).get('oszlop')
    feltetel = session.get('szures', {}).get('feltetel')
    ertek = session.get('szures', {}).get('ertek')
    query = MegmunkalasAdat.query
    if oszlop and feltetel and ertek:
        try:
            column = getattr(MegmunkalasAdat, oszlop)
            value = float(ertek)
            if feltetel == "eq":
                query = query.filter(column == value)
            elif feltetel == "lt":
                query = query.filter(column < value)
            elif feltetel == "gt":
                query = query.filter(column > value)
            elif feltetel == "le":
                query = query.filter(column <= value)
            elif feltetel == "ge":
                query = query.filter(column >= value)
        except Exception:
            logging.error(f"Hibás szűrési feltétel: {oszlop}, {feltetel}, {ertek}") 
            flash("Hibás szűrési feltétel!", "danger")
            return redirect(url_for("eredmenyek"))
        
    adatok = query.order_by(MegmunkalasAdat.datum.desc()).all()

    # Fájl generálása memóriában
    file_data = None
    file_name = ""
    mime_type = ""
    if formatum == "csv":
        output = io.StringIO()
        output.write("ID,Átmérő,Vc,af előtolás,fogszám,fordulat,Gépi előtolás,Dátum\n")
        for adat in adatok:
            output.write(f"{adat.id},{adat.atmero},{adat.vc_inp},{adat.elotolas},{adat.fogsz},{adat.fordulat},{adat.eredmeny2_f},{adat.datum.strftime('%Y-%m-%d %H:%M:%S')}\n")
        file_data = output.getvalue().encode("utf-8")
        file_name = "megmunkalas_adatok.csv"
        mime_type = "text/csv"
    else:  # PDF
       
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        data = [
            ["ID", "Átmérő", "Vc", "aF előtolás", "Fogszám", "Fordulat", "Gépi Előtolás", "Dátum"]
        ]
        for adat in adatok:
            data.append([
                adat.id,
                adat.atmero,
                adat.vc_inp,
                adat.elotolas,
                adat.fogsz,
                adat.fordulat,
                adat.eredmeny2_f,
                adat.datum.strftime("%Y-%m-%d %H:%M:%S")
            ])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ]))
        elements = []
        elements.append(Paragraph("Megmunkálási adatok export", styles["Title"]))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        file_data = buffer.read()
        file_name = "megmunkalas_adatok.pdf"
        mime_type = "application/pdf"

    # Email küldése
    try:
        kuld_email(email, file_data, file_name, mime_type)
        logging.info(f"E-mail küldve: {email}, formátum: {formatum}")
        flash("Az eredményeket elküldtük e-mailben!", "success")
    except Exception:
        logging.error(f"Hiba az e-mail küldésekor: {email}")
        flash("Hiba az e-mail küldésekor!", "danger")

    return redirect(url_for("eredmenyek"))

@app.route("/szuro_torlese", methods=["POST"])
def szuro_torlese():
    if 'user' not in session:
        return redirect("/login")
    session.pop('szures', None)
    logging.info("Szűrés törölve")
    flash("A szűrés törölve lett.", "info")
    return redirect(url_for("eredmenyek"))


@app.route("/torles/<int:id>", methods=["POST"])

def torles(id):

    adat = MegmunkalasAdat.query.get_or_404(id)
    db.session.delete(adat)
    db.session.commit()
    return redirect(url_for("eredmenyek"))
     

@app.route("/export")
def export_csv():
    if 'user' not in session:
        return redirect("/login")
    # Szűrés session-ből
    oszlop = session.get('szures', {}).get('oszlop')
    feltetel = session.get('szures', {}).get('feltetel')
    ertek = session.get('szures', {}).get('ertek')
    query = MegmunkalasAdat.query
    if oszlop and feltetel and ertek:
        try:
            column = getattr(MegmunkalasAdat, oszlop)
            value = float(ertek)
            if feltetel == "eq":
                query = query.filter(column == value)
            elif feltetel == "lt":
                query = query.filter(column < value)
            elif feltetel == "gt":
                query = query.filter(column > value)
            elif feltetel == "le":
                query = query.filter(column <= value)
            elif feltetel == "ge":
                query = query.filter(column >= value)
        except Exception:
            logging.error(f"Hibás szűrési feltétel: {oszlop}, {feltetel}, {ertek}")
            flash("Hibás szűrési feltétel!", "danger")

    adatok = query.order_by(MegmunkalasAdat.datum.desc()).all()

    def generate():
        
        yield "ID,Átmérő,Vc,af előtolás,fogszám,fordulat,Gépi előtolás,Dátum\n"
        for adat in adatok:
            sor = f"{adat.id},{adat.atmero},{adat.vc_inp},{adat.elotolas},{adat.fogsz},{adat.fordulat},{adat.eredmeny2_f},{adat.datum.strftime('%Y-%m-%d %H:%M:%S')}\n"
            yield sor

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=megmunkalas_adatok.csv"})



@app.route("/export_pdf")
def export_pdf():

    if 'user' not in session:
        return redirect("/login")

    buffer = io.BytesIO()

    # 📦 Betűtípus regisztrálása (ékezetekhez)
    font_path = os.path.join("fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVu", font_path))

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # 🧾 Fejléc + adattábla előkészítése
    data = [
        ["ID", "Átmérő", "Vc", "aF előtolás", "Fogszám", "Fordulat", "Gépi Előtolás", "Dátum"]
    ]

    # Szűrés session-ből
    oszlop = session.get('szures', {}).get('oszlop')
    feltetel = session.get('szures', {}).get('feltetel')
    ertek = session.get('szures', {}).get('ertek')
    query = MegmunkalasAdat.query
    if oszlop and feltetel and ertek:
        try:
            column = getattr(MegmunkalasAdat, oszlop)
            value = float(ertek)
            if feltetel == "eq":
                query = query.filter(column == value)
            elif feltetel == "lt":
                query = query.filter(column < value)
            elif feltetel == "gt":
                query = query.filter(column > value)
            elif feltetel == "le":
                query = query.filter(column <= value)
            elif feltetel == "ge":
                query = query.filter(column >= value)
        except Exception:
            logging.error(f"Hibás szűrési feltétel: {oszlop}, {feltetel}, {ertek}")
            flash("Hibás szűrési feltétel!", "danger")

    adatok = query.order_by(MegmunkalasAdat.datum.desc()).all()

    for adat in adatok:
        data.append([
            adat.id,
            adat.atmero,
            adat.vc_inp,
            adat.elotolas,
            adat.fogsz,
            adat.fordulat,
            adat.eredmeny2_f,
            adat.datum.strftime("%Y-%m-%d %H:%M:%S")
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ]))

    elements = []
    elements.append(Paragraph("Megmunkálási adatok export", styles["Title"]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return Response(buffer, mimetype="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=megmunkalas_adatok.pdf"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    #app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))   
    app.run(debug=True)


