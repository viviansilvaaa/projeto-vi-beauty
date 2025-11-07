from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_session import Session
import bcrypt
import secrets
import pymysql.cursors
import pymysql
import os
from functools import wraps

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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
        business_hours = request.form.get('business_hours', '').strip()
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Verifica se já existe um salão com o mesmo nome
            cur.execute("SELECT id FROM salons WHERE name = %s", (name,))
            if cur.fetchone():
                flash('Já existe um salão cadastrado com este nome!', 'error')
                return render_template('register_salon.html')
            
            # Insere o novo salão
            cur.execute(
                "INSERT INTO salons (name, description, address, phone, image_url, business_hours) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, description if description else None, address, phone, image_url, business_hours if business_hours else None)
            )
            connection.commit()
            
            flash('Salão cadastrado com sucesso!', 'success')
            return redirect(url_for('register_salon'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar salão: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    return render_template('register_salon.html')

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
        business_hours = request.form.get('business_hours', '').strip()
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            # Verifica se já existe outro salão com o mesmo nome
            cur.execute("SELECT id FROM salons WHERE name = %s AND id != %s", (name, salon_id))
            if cur.fetchone():
                flash('Já existe outro salão cadastrado com este nome!', 'error')
                return redirect(url_for('edit_salon', salon_id=salon_id))
            
            # Atualiza os dados do salão
            cur.execute(
                "UPDATE salons SET name = %s, description = %s, address = %s, phone = %s, image_url = %s, business_hours = %s WHERE id = %s",
                (name, description if description else None, address, phone, image_url, business_hours if business_hours else None, salon_id)
            )
            connection.commit()
            
            flash('Salão atualizado com sucesso!', 'success')
            return redirect(url_for('list_salons'))
            
        except Exception as e:
            flash(f'Erro ao atualizar salão: {str(e)}', 'error')
        finally:
            if 'connection' in locals():
                connection.close()
            if 'cur' in locals():
                cur.close()
    
    # GET - Busca os dados do salão para edição
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT * FROM salons WHERE id = %s", (salon_id,))
        salon = cur.fetchone()
        
        if not salon:
            flash('Salão não encontrado!', 'error')
            return redirect(url_for('list_salons'))
        
        return render_template('edit_salon.html', salon=salon)
        
    except Exception as e:
        flash(f'Erro ao carregar dados do salão: {str(e)}', 'error')
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
        specialties = request.form.get('specialties', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        image_url = request.form.get('image_url', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validação de campos obrigatórios
        if not salon_id:
            flash('É obrigatório selecionar um salão!', 'error')
            try:
                connection = get_db_connection()
                cur = connection.cursor()
                cur.execute("SELECT id, name FROM salons ORDER BY name ASC")
                salons = cur.fetchall()
                return render_template('register_hairdresser.html', salons=salons)
            except Exception as e:
                flash(f'Erro ao carregar salões: {str(e)}', 'error')
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
                (name, salon_id, specialties if specialties else None, phone, email, image_url if image_url else None, bio if bio else None)
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
    
    # GET - Busca os salões para o formulário
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("SELECT id, name FROM salons ORDER BY name ASC")
        salons = cur.fetchall()
        
        if not salons:
            flash('É necessário cadastrar pelo menos um salão antes de cadastrar cabeleireiros!', 'error')
            return redirect(url_for('register_salon'))
        
        return render_template('register_hairdresser.html', salons=salons)
    except Exception as e:
        flash(f'Erro ao carregar salões: {str(e)}', 'error')
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
        specialties = request.form.get('specialties', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        image_url = request.form.get('image_url', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validação de campos obrigatórios
        if not salon_id:
            flash('É obrigatório selecionar um salão!', 'error')
            return redirect(url_for('edit_hairdresser', hairdresser_id=hairdresser_id))
        
        try:
            connection = get_db_connection()
            cur = connection.cursor()
            
            
            # Atualiza os dados do cabeleireiro
            cur.execute(
                "UPDATE hairdressers SET name = %s, salon_id = %s, specialties = %s, phone = %s, email = %s, image_url = %s, bio = %s WHERE id = %s",
                (name, salon_id, specialties if specialties else None, phone, email, image_url if image_url else None, bio if bio else None, hairdresser_id)
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
    
    # GET - Busca os dados do cabeleireiro e os salões para edição
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT * FROM hairdressers WHERE id = %s", (hairdresser_id,))
        hairdresser = cur.fetchone()
        
        if not hairdresser:
            flash('Cabeleireiro não encontrado!', 'error')
            return redirect(url_for('list_hairdressers'))
        
        cur.execute("SELECT id, name FROM salons ORDER BY name ASC")
        salons = cur.fetchall()
        
        return render_template('edit_hairdresser.html', hairdresser=hairdresser, salons=salons)
        
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

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))