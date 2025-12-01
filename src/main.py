from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_session import Session
import bcrypt
import secrets
import pymysql.cursors
import pymysql
import os
from functools import wraps
from datetime import datetime, date, timedelta

# Lista fixa de especialidades disponiveis para cabeleireiros
SPECIALTIES_LIST = [
    'Corte Masculino',
    'Corte Feminino',
    'Coloracao',
    'Hidratacao',
    'Escova',
    'Alisamento',
    'Penteado',
    'Manicure',
    'Pedicure',
    'Barba',
    'Design de Sobrancelha',
    'Maquiagem'
]

# Lista de dias da semana para horario de funcionamento
WEEKDAYS = [
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terca-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sabado'),
    ('domingo', 'Domingo')
]

# Mapeamento de dia da semana para numero (0=segunda, 6=domingo)
WEEKDAY_TO_NUM = {
    'segunda': 0,
    'terca': 1,
    'quarta': 2,
    'quinta': 3,
    'sexta': 4,
    'sabado': 5,
    'domingo': 6
}

# Mapeamento inverso (numero para dia da semana)
NUM_TO_WEEKDAY = {v: k for k, v in WEEKDAY_TO_NUM.items()}

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Filtro Jinja2 para formatar timedelta como hora
@app.template_filter('format_time')
def format_time(td):
    """Converte timedelta para string de hora HH:MM"""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    return str(td)

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'vivian_user'),
    'password': os.getenv('DB_PASSWORD', 'vivian_password'),
    'db': os.getenv('DB_NAME', 'users'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """Cria uma nova conexão com o banco de dados"""
    return pymysql.connect(**DB_CONFIG)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session['user_id'] != 1:
            flash('Acesso negado! Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('profile'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Verifica senha com compatibilidade para texto plano e bcrypt"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        return password == hashed

# ROTAS WEB FRONTEND
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Busca usuário por email
            cur.execute("SELECT id, name, email, password FROM users_data WHERE email = %s", (email,))
            user = cur.fetchone()
            
            if user and check_password(password, user['password']):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Email ou senha incorretos!', 'error')
                
        except Exception as e:
            flash(f'Erro no sistema: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cpf = request.form['cpf']
        password = request.form['password']
        gender = request.form['gender']
        phone = request.form['phone']
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Verifica se email já existe
            cur.execute("SELECT id FROM users_data WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Este email já está cadastrado!', 'error')
                return render_template('register.html')
            
            # Verifica se CPF já existe
            cur.execute("SELECT id FROM users_data WHERE cpf = %s", (cpf,))
            if cur.fetchone():
                flash('Este CPF já está cadastrado!', 'error')
                return render_template('register.html')
            
            # Hash da senha e inserção no banco
            hashed_password = hash_password(password)
            cur.execute(
                "INSERT INTO users_data (name, email, cpf, password, gender, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, cpf, hashed_password, gender, phone)
            )
            connection.commit()
            
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Busca dados completos do usuário
        cur.execute("SELECT * FROM users_data WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        return render_template('profile.html', user=user)
        
    except Exception as e:
        flash(f'Erro ao carregar perfil: {str(e)}', 'error')
        return redirect(url_for('login'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o email já existe para outro usuário
        cur.execute("SELECT id FROM users_data WHERE email = %s AND id != %s", (email, session['user_id']))
        if cur.fetchone():
            flash('Este email já está em uso por outro usuário!', 'error')
            return redirect(url_for('profile'))
        
        # Atualiza os dados
        cur.execute(
            "UPDATE users_data SET name = %s, email = %s, phone = %s WHERE id = %s",
            (name, email, phone, session['user_id'])
        )
        connection.commit()
        
        # Atualiza a sessão
        session['user_name'] = name
        session['user_email'] = email
        
        flash('Perfil atualizado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('profile'))

@app.route('/register_salon', methods=['GET', 'POST'])
@admin_required
def register_salon():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        image_url = request.form.get('image_url', '').strip()
        opening_day = request.form.get('opening_day', 'segunda').strip()
        closing_day = request.form.get('closing_day', 'sexta').strip()
        opening_time = request.form.get('opening_time', '09:00').strip()
        closing_time = request.form.get('closing_time', '18:00').strip()
        
        # Valida os dias da semana
        valid_days = [d[0] for d in WEEKDAYS]
        if opening_day not in valid_days:
            opening_day = 'segunda'
        if closing_day not in valid_days:
            closing_day = 'sexta'
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Verifica se ja existe um salao com o mesmo nome
            cur.execute("SELECT id FROM salons WHERE name = %s", (name,))
            if cur.fetchone():
                flash('Ja existe um salao cadastrado com este nome!', 'error')
                return render_template('register_salon.html', weekdays=WEEKDAYS)
            
            # Insere o novo salao
            cur.execute(
                "INSERT INTO salons (name, description, address, phone, image_url, opening_day, closing_day, opening_time, closing_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (name, description if description else None, address, phone, image_url, opening_day, closing_day, opening_time, closing_time)
            )
            connection.commit()
            
            flash('Salao cadastrado com sucesso!', 'success')
            return redirect(url_for('register_salon'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar salao: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    return render_template('register_salon.html', weekdays=WEEKDAYS)

@app.route('/list_salons')
@admin_required
def list_salons():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Busca todos os salões ordenados por nome
        cur.execute("SELECT * FROM salons ORDER BY name ASC")
        salons = cur.fetchall()
        
        return render_template('list_salons.html', salons=salons)
        
    except Exception as e:
        flash(f'Erro ao carregar salões: {str(e)}', 'error')
        return redirect(url_for('profile'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/edit_salon/<int:salon_id>', methods=['GET', 'POST'])
@admin_required
def edit_salon(salon_id):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        image_url = request.form.get('image_url', '').strip()
        opening_day = request.form.get('opening_day', 'segunda').strip()
        closing_day = request.form.get('closing_day', 'sexta').strip()
        opening_time = request.form.get('opening_time', '09:00').strip()
        closing_time = request.form.get('closing_time', '18:00').strip()
        
        # Valida os dias da semana
        valid_days = [d[0] for d in WEEKDAYS]
        if opening_day not in valid_days:
            opening_day = 'segunda'
        if closing_day not in valid_days:
            closing_day = 'sexta'
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Verifica se ja existe outro salao com o mesmo nome
            cur.execute("SELECT id FROM salons WHERE name = %s AND id != %s", (name, salon_id))
            if cur.fetchone():
                flash('Ja existe outro salao cadastrado com este nome!', 'error')
                return redirect(url_for('edit_salon', salon_id=salon_id))
            
            # Atualiza os dados do salao
            cur.execute(
                "UPDATE salons SET name = %s, description = %s, address = %s, phone = %s, image_url = %s, opening_day = %s, closing_day = %s, opening_time = %s, closing_time = %s WHERE id = %s",
                (name, description if description else None, address, phone, image_url, opening_day, closing_day, opening_time, closing_time, salon_id)
            )
            connection.commit()
            
            flash('Salao atualizado com sucesso!', 'success')
            return redirect(url_for('list_salons'))
            
        except Exception as e:
            flash(f'Erro ao atualizar salao: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    # GET - Busca os dados do salao para edicao
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT * FROM salons WHERE id = %s", (salon_id,))
        salon = cur.fetchone()
        
        if not salon:
            flash('Salao nao encontrado!', 'error')
            return redirect(url_for('list_salons'))
        
        return render_template('edit_salon.html', salon=salon, weekdays=WEEKDAYS)
        
    except Exception as e:
        flash(f'Erro ao carregar dados do salao: {str(e)}', 'error')
        return redirect(url_for('list_salons'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/delete_salon/<int:salon_id>', methods=['POST'])
@admin_required
def delete_salon(salon_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o salão existe
        cur.execute("SELECT name FROM salons WHERE id = %s", (salon_id,))
        salon = cur.fetchone()
        
        if not salon:
            flash('Salão não encontrado!', 'error')
            return redirect(url_for('list_salons'))
        
        # Deleta o salão
        cur.execute("DELETE FROM salons WHERE id = %s", (salon_id,))
        connection.commit()
        
        flash(f'Salão "{salon["name"]}" excluído com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao excluir salão: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('list_salons'))

@app.route('/register_hairdresser', methods=['GET', 'POST'])
@admin_required
def register_hairdresser():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        salon_id = request.form.get('salon_id', '').strip()
        # Pega as especialidades selecionadas como lista
        specialties_list = request.form.getlist('specialties')
        # Filtra apenas valores validos e junta com virgula para o SET do MySQL
        specialties = ','.join([s for s in specialties_list if s in SPECIALTIES_LIST]) if specialties_list else None
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        image_url = request.form.get('image_url', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validacao de campos obrigatorios
        if not salon_id:
            flash('E obrigatorio selecionar um salao!', 'error')
            try:
                connection = get_db_connection()
                cur = connection.cursor()
                cur.execute("SELECT id, name FROM salons ORDER BY name ASC")
                salons = cur.fetchall()
                return render_template('register_hairdresser.html', salons=salons, specialties_list=SPECIALTIES_LIST)
            except Exception as e:
                flash(f'Erro ao carregar saloes: {str(e)}', 'error')
                return redirect(url_for('list_salons'))
            finally:
                if 'connection' in locals():
                    connection.close()
                if 'cur' in locals():
                    cur.close()
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Insere o novo cabeleireiro
            cur.execute(
                "INSERT INTO hairdressers (name, salon_id, specialties, phone, email, image_url, bio) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, salon_id, specialties, phone, email, image_url if image_url else None, bio if bio else None)
            )
            connection.commit()
            
            flash('Cabeleireiro cadastrado com sucesso!', 'success')
            return redirect(url_for('register_hairdresser'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar cabeleireiro: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    # GET - Busca os saloes para o formulario
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("SELECT id, name FROM salons ORDER BY name ASC")
        salons = cur.fetchall()
        
        if not salons:
            flash('E necessario cadastrar pelo menos um salao antes de cadastrar cabeleireiros!', 'error')
            return redirect(url_for('register_salon'))
        
        return render_template('register_hairdresser.html', salons=salons, specialties_list=SPECIALTIES_LIST)
    except Exception as e:
        flash(f'Erro ao carregar saloes: {str(e)}', 'error')
        return redirect(url_for('list_salons'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/list_hairdressers')
@admin_required
def list_hairdressers():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Busca todos os cabeleireiros com informações do salão
        cur.execute("""
            SELECT h.*, s.name as salon_name 
            FROM hairdressers h 
            INNER JOIN salons s ON h.salon_id = s.id 
            ORDER BY s.name ASC, h.name ASC
        """)
        hairdressers = cur.fetchall()
        
        return render_template('list_hairdressers.html', hairdressers=hairdressers)
        
    except Exception as e:
        flash(f'Erro ao carregar cabeleireiros: {str(e)}', 'error')
        return redirect(url_for('profile'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/edit_hairdresser/<int:hairdresser_id>', methods=['GET', 'POST'])
@admin_required
def edit_hairdresser(hairdresser_id):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        salon_id = request.form.get('salon_id', '').strip()
        # Pega as especialidades selecionadas como lista
        specialties_list = request.form.getlist('specialties')
        # Filtra apenas valores validos e junta com virgula para o SET do MySQL
        specialties = ','.join([s for s in specialties_list if s in SPECIALTIES_LIST]) if specialties_list else None
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        image_url = request.form.get('image_url', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validacao de campos obrigatorios
        if not salon_id:
            flash('E obrigatorio selecionar um salao!', 'error')
            return redirect(url_for('edit_hairdresser', hairdresser_id=hairdresser_id))
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Atualiza os dados do cabeleireiro
            cur.execute(
                "UPDATE hairdressers SET name = %s, salon_id = %s, specialties = %s, phone = %s, email = %s, image_url = %s, bio = %s WHERE id = %s",
                (name, salon_id, specialties, phone, email, image_url if image_url else None, bio if bio else None, hairdresser_id)
            )
            connection.commit()
            
            flash('Cabeleireiro atualizado com sucesso!', 'success')
            return redirect(url_for('list_hairdressers'))
            
        except Exception as e:
            flash(f'Erro ao atualizar cabeleireiro: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    # GET - Busca os dados do cabeleireiro e os saloes para edicao
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT * FROM hairdressers WHERE id = %s", (hairdresser_id,))
        hairdresser = cur.fetchone()
        
        if not hairdresser:
            flash('Cabeleireiro nao encontrado!', 'error')
            return redirect(url_for('list_hairdressers'))
        
        # Converte as especialidades do cabeleireiro para lista para marcar os checkboxes
        hairdresser_specialties = hairdresser['specialties'].split(',') if hairdresser['specialties'] else []
        
        cur.execute("SELECT id, name FROM salons ORDER BY name ASC")
        salons = cur.fetchall()
        
        return render_template('edit_hairdresser.html', hairdresser=hairdresser, salons=salons, specialties_list=SPECIALTIES_LIST, hairdresser_specialties=hairdresser_specialties)
        
    except Exception as e:
        flash(f'Erro ao carregar dados do cabeleireiro: {str(e)}', 'error')
        return redirect(url_for('list_hairdressers'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/delete_hairdresser/<int:hairdresser_id>', methods=['POST'])
@admin_required
def delete_hairdresser(hairdresser_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o cabeleireiro existe
        cur.execute("SELECT name FROM hairdressers WHERE id = %s", (hairdresser_id,))
        hairdresser = cur.fetchone()
        
        if not hairdresser:
            flash('Cabeleireiro não encontrado!', 'error')
            return redirect(url_for('list_hairdressers'))
        
        # Deleta o cabeleireiro
        cur.execute("DELETE FROM hairdressers WHERE id = %s", (hairdresser_id,))
        connection.commit()
        
        flash(f'Cabeleireiro "{hairdresser["name"]}" excluído com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao excluir cabeleireiro: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('list_hairdressers'))

@app.route('/appointments')
@login_required
def appointments():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Busca todos os agendamentos do usuário com informações do salão e cabeleireiro
        cur.execute("""
            SELECT a.*, 
                   s.name as salon_name, 
                   h.name as hairdresser_name
            FROM appointments a
            INNER JOIN salons s ON a.salon_id = s.id
            INNER JOIN hairdressers h ON a.hairdresser_id = h.id
            WHERE a.user_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (session['user_id'],))
        user_appointments = cur.fetchall()
        
        # Busca todos os salões para o formulário
        cur.execute("SELECT id, name, address FROM salons ORDER BY name ASC")
        salons = cur.fetchall()
        
        # Obtém a data atual para validação no frontend
        today = date.today().isoformat()
        
        return render_template('appointments.html', appointments=user_appointments, salons=salons, today=today)
        
    except Exception as e:
        flash(f'Erro ao carregar agendamentos: {str(e)}', 'error')
        return redirect(url_for('profile'))
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/api/hairdressers_by_salon/<int:salon_id>')
@login_required
def get_hairdressers_by_salon(salon_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Busca cabeleireiros do salao
        cur.execute("""
            SELECT id, name, specialties 
            FROM hairdressers 
            WHERE salon_id = %s 
            ORDER BY name ASC
        """, (salon_id,))
        hairdressers = cur.fetchall()
        
        return jsonify(hairdressers)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/api/salon_schedule/<int:salon_id>')
@login_required
def get_salon_schedule(salon_id):
    """Retorna informacoes de horario de funcionamento do salao"""
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("""
            SELECT opening_day, closing_day, opening_time, closing_time 
            FROM salons 
            WHERE id = %s
        """, (salon_id,))
        salon = cur.fetchone()
        
        if not salon:
            return jsonify({'error': 'Salao nao encontrado'}), 404
        
        # Converte timedelta para string de hora
        opening_time = salon['opening_time']
        closing_time = salon['closing_time']
        
        if isinstance(opening_time, timedelta):
            total_seconds = int(opening_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            opening_time = f"{hours:02d}:{minutes:02d}"
        else:
            opening_time = str(opening_time)[:5]
            
        if isinstance(closing_time, timedelta):
            total_seconds = int(closing_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            closing_time = f"{hours:02d}:{minutes:02d}"
        else:
            closing_time = str(closing_time)[:5]
        
        return jsonify({
            'opening_day': salon['opening_day'],
            'closing_day': salon['closing_day'],
            'opening_time': opening_time,
            'closing_time': closing_time,
            'opening_day_num': WEEKDAY_TO_NUM.get(salon['opening_day'], 0),
            'closing_day_num': WEEKDAY_TO_NUM.get(salon['closing_day'], 4)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/api/available_times/<int:hairdresser_id>/<appointment_date>')
@login_required
def get_available_times(hairdresser_id, appointment_date):
    """Retorna horarios disponiveis para um cabeleireiro em uma data especifica"""
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Busca o salao do cabeleireiro e horarios de funcionamento
        cur.execute("""
            SELECT s.opening_day, s.closing_day, s.opening_time, s.closing_time 
            FROM hairdressers h
            INNER JOIN salons s ON h.salon_id = s.id
            WHERE h.id = %s
        """, (hairdresser_id,))
        salon = cur.fetchone()
        
        if not salon:
            return jsonify({'error': 'Cabeleireiro nao encontrado'}), 404
        
        # Converte a data para verificar o dia da semana
        try:
            date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Data invalida'}), 400
        
        # Pega o dia da semana (0=segunda, 6=domingo)
        weekday_num = date_obj.weekday()
        
        # Verifica se o dia esta dentro do intervalo de funcionamento
        opening_day_num = WEEKDAY_TO_NUM.get(salon['opening_day'], 0)
        closing_day_num = WEEKDAY_TO_NUM.get(salon['closing_day'], 4)
        
        # Verifica se o salao funciona neste dia
        if closing_day_num >= opening_day_num:
            # Intervalo normal (ex: segunda a sexta)
            if weekday_num < opening_day_num or weekday_num > closing_day_num:
                return jsonify({'available_times': [], 'message': 'Salao fechado neste dia'})
        else:
            # Intervalo que atravessa o fim de semana (ex: quinta a terca)
            if weekday_num > closing_day_num and weekday_num < opening_day_num:
                return jsonify({'available_times': [], 'message': 'Salao fechado neste dia'})
        
        # Converte horarios de funcionamento
        opening_time = salon['opening_time']
        closing_time = salon['closing_time']
        
        if isinstance(opening_time, timedelta):
            opening_minutes = int(opening_time.total_seconds() // 60)
        else:
            parts = str(opening_time).split(':')
            opening_minutes = int(parts[0]) * 60 + int(parts[1])
            
        if isinstance(closing_time, timedelta):
            closing_minutes = int(closing_time.total_seconds() // 60)
        else:
            parts = str(closing_time).split(':')
            closing_minutes = int(parts[0]) * 60 + int(parts[1])
        
        # Gera todos os horarios possiveis em intervalos de 30 minutos
        all_times = []
        current_minutes = opening_minutes
        while current_minutes < closing_minutes:
            hours = current_minutes // 60
            mins = current_minutes % 60
            all_times.append(f"{hours:02d}:{mins:02d}")
            current_minutes += 30
        
        # Busca agendamentos existentes para este cabeleireiro nesta data
        cur.execute("""
            SELECT appointment_time 
            FROM appointments 
            WHERE hairdresser_id = %s 
            AND appointment_date = %s 
            AND status != 'cancelled'
        """, (hairdresser_id, appointment_date))
        booked_appointments = cur.fetchall()
        
        # Converte horarios agendados para set de strings
        booked_times = set()
        for apt in booked_appointments:
            apt_time = apt['appointment_time']
            if isinstance(apt_time, timedelta):
                total_seconds = int(apt_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                booked_times.add(f"{hours:02d}:{minutes:02d}")
            else:
                booked_times.add(str(apt_time)[:5])
        
        # Filtra horarios disponiveis
        available_times = [t for t in all_times if t not in booked_times]
        
        # Se for hoje, remove horarios que ja passaram
        today = date.today()
        if date_obj == today:
            now = datetime.now()
            current_time_str = f"{now.hour:02d}:{now.minute:02d}"
            available_times = [t for t in available_times if t > current_time_str]
        
        return jsonify({'available_times': available_times})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()

@app.route('/create_appointment', methods=['POST'])
@login_required
def create_appointment():
    salon_id = request.form.get('salon_id', '').strip()
    hairdresser_id = request.form.get('hairdresser_id', '').strip()
    appointment_date = request.form.get('appointment_date', '').strip()
    appointment_time = request.form.get('appointment_time', '').strip()
    service_type = request.form.get('service_type', '').strip()
    notes = request.form.get('notes', '').strip()
    
    # Validação de campos obrigatórios
    if not salon_id or not hairdresser_id or not appointment_date or not appointment_time or not service_type:
        flash('Todos os campos obrigatórios devem ser preenchidos!', 'error')
        return redirect(url_for('appointments'))
    
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o cabeleireiro pertence ao salão
        cur.execute("SELECT id FROM hairdressers WHERE id = %s AND salon_id = %s", (hairdresser_id, salon_id))
        if not cur.fetchone():
            flash('Cabeleireiro não pertence ao salão selecionado!', 'error')
            return redirect(url_for('appointments'))
        
        # Verifica se já existe um agendamento para o mesmo horário
        cur.execute("""
            SELECT id FROM appointments 
            WHERE hairdresser_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s 
            AND status != 'cancelled'
        """, (hairdresser_id, appointment_date, appointment_time))
        
        if cur.fetchone():
            flash('Este horário já está reservado! Por favor, escolha outro horário.', 'error')
            return redirect(url_for('appointments'))
        
        # Insere o novo agendamento
        cur.execute("""
            INSERT INTO appointments (user_id, salon_id, hairdresser_id, appointment_date, appointment_time, service_type, notes, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'confirmed')
        """, (session['user_id'], salon_id, hairdresser_id, appointment_date, appointment_time, service_type, notes if notes else None))
        connection.commit()
        
        flash('Agendamento realizado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao criar agendamento: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('appointments'))

@app.route('/update_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def update_appointment(appointment_id):
    salon_id = request.form.get('salon_id', '').strip()
    hairdresser_id = request.form.get('hairdresser_id', '').strip()
    appointment_date = request.form.get('appointment_date', '').strip()
    appointment_time = request.form.get('appointment_time', '').strip()
    service_type = request.form.get('service_type', '').strip()
    notes = request.form.get('notes', '').strip()
    
    # Validação de campos obrigatórios
    if not salon_id or not hairdresser_id or not appointment_date or not appointment_time or not service_type:
        flash('Todos os campos obrigatórios devem ser preenchidos!', 'error')
        return redirect(url_for('appointments'))
    
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o agendamento pertence ao usuário
        cur.execute("SELECT id FROM appointments WHERE id = %s AND user_id = %s", (appointment_id, session['user_id']))
        if not cur.fetchone():
            flash('Agendamento não encontrado ou você não tem permissão para editá-lo!', 'error')
            return redirect(url_for('appointments'))
        
        # Verifica se o cabeleireiro pertence ao salão
        cur.execute("SELECT id FROM hairdressers WHERE id = %s AND salon_id = %s", (hairdresser_id, salon_id))
        if not cur.fetchone():
            flash('Cabeleireiro não pertence ao salão selecionado!', 'error')
            return redirect(url_for('appointments'))
        
        # Verifica se já existe um agendamento para o mesmo horário (exceto o atual)
        cur.execute("""
            SELECT id FROM appointments 
            WHERE hairdresser_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s 
            AND id != %s
            AND status != 'cancelled'
        """, (hairdresser_id, appointment_date, appointment_time, appointment_id))
        
        if cur.fetchone():
            flash('Este horário já está reservado! Por favor, escolha outro horário.', 'error')
            return redirect(url_for('appointments'))
        
        # Atualiza o agendamento
        cur.execute("""
            UPDATE appointments 
            SET salon_id = %s, hairdresser_id = %s, appointment_date = %s, appointment_time = %s, service_type = %s, notes = %s
            WHERE id = %s AND user_id = %s
        """, (salon_id, hairdresser_id, appointment_date, appointment_time, service_type, notes if notes else None, appointment_id, session['user_id']))
        connection.commit()
        
        flash('Agendamento atualizado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao atualizar agendamento: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('appointments'))

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o agendamento pertence ao usuário
        cur.execute("SELECT id, status FROM appointments WHERE id = %s AND user_id = %s", (appointment_id, session['user_id']))
        appointment = cur.fetchone()
        
        if not appointment:
            flash('Agendamento não encontrado ou você não tem permissão para cancelá-lo!', 'error')
            return redirect(url_for('appointments'))
        
        if appointment['status'] == 'cancelled':
            flash('Este agendamento já está cancelado!', 'error')
            return redirect(url_for('appointments'))
        
        # Cancela o agendamento
        cur.execute("UPDATE appointments SET status = 'cancelled' WHERE id = %s", (appointment_id,))
        connection.commit()
        
        flash('Agendamento cancelado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao cancelar agendamento: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('appointments'))

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verifica se o agendamento pertence ao usuário
        cur.execute("SELECT id FROM appointments WHERE id = %s AND user_id = %s", (appointment_id, session['user_id']))
        if not cur.fetchone():
            flash('Agendamento não encontrado ou você não tem permissão para excluí-lo!', 'error')
            return redirect(url_for('appointments'))
        
        # Deleta o agendamento
        cur.execute("DELETE FROM appointments WHERE id = %s AND user_id = %s", (appointment_id, session['user_id']))
        connection.commit()
        
        flash('Agendamento excluído com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao excluir agendamento: {str(e)}', 'error')
    finally:
        if 'connection' in locals():
            connection.close()
        if 'cur' in locals():
            cur.close()
    
    return redirect(url_for('appointments'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))