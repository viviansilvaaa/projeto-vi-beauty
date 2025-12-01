// Armazena os dados dos cabeleireiros e saloes carregados
let hairdressersData = {};
let salonScheduleData = {};

// Funcoes para controlar modais
function openCreateModal() {
    document.getElementById('createModal').style.display = 'block';
}

function closeCreateModal() {
    document.getElementById('createModal').style.display = 'none';
    document.querySelector('#createModal form').reset();
    document.getElementById('hairdresser_id').disabled = true;
    document.getElementById('hairdresser_id').innerHTML = '<option value="">Selecione um salao primeiro</option>';
    document.getElementById('service_type').disabled = true;
    document.getElementById('service_type').innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
    document.getElementById('appointment_time').disabled = true;
    document.getElementById('appointment_time').innerHTML = '<option value="">Selecione cabeleireiro e data primeiro</option>';
}

function openEditModal(id, salonId, hairdresserId, date, time, serviceType, notes) {
    document.getElementById('editModal').style.display = 'block';
    document.getElementById('editForm').action = `/update_appointment/${id}`;
    
    // Preenche os campos
    document.getElementById('edit_salon_id').value = salonId;
    
    // Formata a data (de YYYY-MM-DD para o formato esperado pelo input date)
    const formattedDate = date.split(' ')[0]; // Remove a hora se houver
    document.getElementById('edit_appointment_date').value = formattedDate;
    
    // Armazena o horario atual para selecionar depois
    const formattedTime = time.split(':').slice(0, 2).join(':');
    
    document.getElementById('edit_notes').value = notes;
    
    // Carrega os cabeleireiros do salao e depois seleciona o correto
    // Passa o horario e servico para pre-selecionar
    loadHairdressers(salonId, 'edit', hairdresserId, serviceType, formattedTime);
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    document.querySelector('#editModal form').reset();
    document.getElementById('edit_service_type').disabled = true;
    document.getElementById('edit_service_type').innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
    document.getElementById('edit_appointment_time').disabled = true;
    document.getElementById('edit_appointment_time').innerHTML = '<option value="">Selecione cabeleireiro e data primeiro</option>';
}

// Fecha o modal ao clicar fora dele
window.onclick = function(event) {
    const createModal = document.getElementById('createModal');
    const editModal = document.getElementById('editModal');
    
    if (event.target == createModal) {
        closeCreateModal();
    }
    if (event.target == editModal) {
        closeEditModal();
    }
}

// Carrega informacoes do horario de funcionamento do salao
async function loadSalonSchedule(salonId, context) {
    if (!salonId) return null;
    
    try {
        const response = await fetch(`/api/salon_schedule/${salonId}`);
        const schedule = await response.json();
        
        if (schedule.error) {
            console.error('Erro ao carregar horario do salao:', schedule.error);
            return null;
        }
        
        salonScheduleData[context] = schedule;
        return schedule;
        
    } catch (error) {
        console.error('Erro ao carregar horario do salao:', error);
        return null;
    }
}

// Carrega cabeleireiros por salao
async function loadHairdressers(salonId, context, selectedHairdresserId = null, selectedServiceType = null, selectedTime = null) {
    const selectId = context === 'create' ? 'hairdresser_id' : 'edit_hairdresser_id';
    const serviceSelectId = context === 'create' ? 'service_type' : 'edit_service_type';
    const timeSelectId = context === 'create' ? 'appointment_time' : 'edit_appointment_time';
    const select = document.getElementById(selectId);
    const serviceSelect = document.getElementById(serviceSelectId);
    const timeSelect = document.getElementById(timeSelectId);
    
    if (!salonId) {
        select.disabled = true;
        select.innerHTML = '<option value="">Selecione um salao primeiro</option>';
        serviceSelect.disabled = true;
        serviceSelect.innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">Selecione cabeleireiro e data primeiro</option>';
        return;
    }
    
    // Carrega horario de funcionamento do salao
    await loadSalonSchedule(salonId, context);
    
    try {
        const response = await fetch(`/api/hairdressers_by_salon/${salonId}`);
        const hairdressers = await response.json();
        
        if (hairdressers.error) {
            alert('Erro ao carregar cabeleireiros: ' + hairdressers.error);
            return;
        }
        
        // Armazena os dados para uso posterior
        hairdressersData[context] = {};
        hairdressers.forEach(h => {
            hairdressersData[context][h.id] = h;
        });
        
        select.innerHTML = '<option value="">Selecione um cabeleireiro</option>';
        
        if (hairdressers.length === 0) {
            select.innerHTML = '<option value="">Nenhum cabeleireiro disponivel neste salao</option>';
            select.disabled = true;
            serviceSelect.disabled = true;
            serviceSelect.innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
            timeSelect.disabled = true;
            timeSelect.innerHTML = '<option value="">Selecione cabeleireiro e data primeiro</option>';
            return;
        }
        
        hairdressers.forEach(hairdresser => {
            const option = document.createElement('option');
            option.value = hairdresser.id;
            
            let text = hairdresser.name;
            if (hairdresser.specialties) {
                text += ` - ${hairdresser.specialties}`;
            }
            option.textContent = text;
            
            // Se foi fornecido um ID para selecionar, marca essa opcao
            if (selectedHairdresserId && hairdresser.id == selectedHairdresserId) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });
        
        select.disabled = false;
        
        // Se um cabeleireiro foi pre-selecionado, carrega os servicos e horarios
        if (selectedHairdresserId) {
            loadServices(selectedHairdresserId, context, selectedServiceType);
            // Carrega horarios disponiveis se tiver data selecionada
            const dateId = context === 'create' ? 'appointment_date' : 'edit_appointment_date';
            const dateValue = document.getElementById(dateId).value;
            if (dateValue) {
                loadAvailableTimes(context, selectedTime);
            }
        } else {
            serviceSelect.disabled = true;
            serviceSelect.innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
            timeSelect.disabled = true;
            timeSelect.innerHTML = '<option value="">Selecione cabeleireiro e data primeiro</option>';
        }
        
    } catch (error) {
        console.error('Erro ao carregar cabeleireiros:', error);
        alert('Erro ao carregar cabeleireiros. Por favor, tente novamente.');
    }
}

// Carrega os servicos baseados nas especialidades do cabeleireiro
function loadServices(hairdresserId, context, selectedServiceType = null) {
    const serviceSelectId = context === 'create' ? 'service_type' : 'edit_service_type';
    const serviceSelect = document.getElementById(serviceSelectId);
    
    if (!hairdresserId) {
        serviceSelect.disabled = true;
        serviceSelect.innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
        return;
    }
    
    const hairdresser = hairdressersData[context][hairdresserId];
    
    if (!hairdresser) {
        serviceSelect.disabled = true;
        serviceSelect.innerHTML = '<option value="">Selecione um cabeleireiro primeiro</option>';
        return;
    }
    
    serviceSelect.innerHTML = '<option value="">Selecione um servico</option>';
    
    // Se o cabeleireiro tem especialidades, mostra apenas elas
    if (hairdresser.specialties) {
        const specialties = hairdresser.specialties.split(',');
        
        if (specialties.length === 0) {
            serviceSelect.innerHTML = '<option value="">Este cabeleireiro nao tem especialidades cadastradas</option>';
            serviceSelect.disabled = true;
            return;
        }
        
        specialties.forEach(specialty => {
            const option = document.createElement('option');
            option.value = specialty.trim();
            option.textContent = specialty.trim();
            
            // Se foi fornecido um servico para selecionar, marca essa opcao
            if (selectedServiceType && specialty.trim() === selectedServiceType) {
                option.selected = true;
            }
            
            serviceSelect.appendChild(option);
        });
        
        serviceSelect.disabled = false;
    } else {
        serviceSelect.innerHTML = '<option value="">Este cabeleireiro nao tem especialidades cadastradas</option>';
        serviceSelect.disabled = true;
    }
    
    // Tenta carregar os horarios disponiveis se ja tiver data selecionada
    const dateId = context === 'create' ? 'appointment_date' : 'edit_appointment_date';
    const dateValue = document.getElementById(dateId).value;
    if (dateValue) {
        loadAvailableTimes(context);
    }
}

// Carrega os horarios disponiveis para o cabeleireiro na data selecionada
async function loadAvailableTimes(context, selectedTime = null) {
    const hairdresserSelectId = context === 'create' ? 'hairdresser_id' : 'edit_hairdresser_id';
    const dateId = context === 'create' ? 'appointment_date' : 'edit_appointment_date';
    const timeSelectId = context === 'create' ? 'appointment_time' : 'edit_appointment_time';
    
    const hairdresserId = document.getElementById(hairdresserSelectId).value;
    const appointmentDate = document.getElementById(dateId).value;
    const timeSelect = document.getElementById(timeSelectId);
    
    if (!hairdresserId || !appointmentDate) {
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">Selecione cabeleireiro e data primeiro</option>';
        return;
    }
    
    // Verifica se a data selecionada e um dia valido de funcionamento
    const schedule = salonScheduleData[context];
    if (schedule) {
        const dateObj = new Date(appointmentDate + 'T12:00:00');
        const weekdayNum = dateObj.getDay();
        // Converte de domingo=0 para segunda=0
        const adjustedWeekday = weekdayNum === 0 ? 6 : weekdayNum - 1;
        
        const openingDayNum = schedule.opening_day_num;
        const closingDayNum = schedule.closing_day_num;
        
        let isValidDay = false;
        if (closingDayNum >= openingDayNum) {
            // Intervalo normal (ex: segunda a sexta)
            isValidDay = adjustedWeekday >= openingDayNum && adjustedWeekday <= closingDayNum;
        } else {
            // Intervalo que atravessa o fim de semana (ex: quinta a terca)
            isValidDay = adjustedWeekday >= openingDayNum || adjustedWeekday <= closingDayNum;
        }
        
        if (!isValidDay) {
            timeSelect.disabled = true;
            timeSelect.innerHTML = '<option value="">Salao fechado neste dia</option>';
            return;
        }
    }
    
    try {
        timeSelect.innerHTML = '<option value="">Carregando horarios...</option>';
        
        const response = await fetch(`/api/available_times/${hairdresserId}/${appointmentDate}`);
        const data = await response.json();
        
        if (data.error) {
            timeSelect.innerHTML = `<option value="">${data.error}</option>`;
            timeSelect.disabled = true;
            return;
        }
        
        if (data.message) {
            timeSelect.innerHTML = `<option value="">${data.message}</option>`;
            timeSelect.disabled = true;
            return;
        }
        
        const availableTimes = data.available_times;
        
        if (availableTimes.length === 0) {
            timeSelect.innerHTML = '<option value="">Nenhum horario disponivel nesta data</option>';
            timeSelect.disabled = true;
            return;
        }
        
        timeSelect.innerHTML = '<option value="">Selecione um horario</option>';
        
        availableTimes.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            
            // Se foi fornecido um horario para selecionar, marca essa opcao
            if (selectedTime && time === selectedTime) {
                option.selected = true;
            }
            
            timeSelect.appendChild(option);
        });
        
        // Se o horario selecionado nao esta disponivel, adiciona como opcao
        if (selectedTime && !availableTimes.includes(selectedTime)) {
            const option = document.createElement('option');
            option.value = selectedTime;
            option.textContent = `${selectedTime} (horario atual)`;
            option.selected = true;
            timeSelect.appendChild(option);
        }
        
        timeSelect.disabled = false;
        
    } catch (error) {
        console.error('Erro ao carregar horarios:', error);
        timeSelect.innerHTML = '<option value="">Erro ao carregar horarios</option>';
        timeSelect.disabled = true;
    }
}

// Validacao do formulario de criar
function validateForm() {
    const salonId = document.getElementById('salon_id').value;
    const hairdresserId = document.getElementById('hairdresser_id').value;
    const date = document.getElementById('appointment_date').value;
    const time = document.getElementById('appointment_time').value;
    const serviceType = document.getElementById('service_type').value;
    
    if (!salonId || !hairdresserId || !date || !time || !serviceType) {
        alert('Por favor, preencha todos os campos obrigatorios!');
        return false;
    }
    
    // Valida se a data nao e no passado
    const selectedDate = new Date(date + 'T' + time);
    const now = new Date();
    
    if (selectedDate < now) {
        alert('A data e hora do agendamento nao podem ser no passado!');
        return false;
    }
    
    return true;
}

// Validacao do formulario de editar
function validateEditForm() {
    const salonId = document.getElementById('edit_salon_id').value;
    const hairdresserId = document.getElementById('edit_hairdresser_id').value;
    const date = document.getElementById('edit_appointment_date').value;
    const time = document.getElementById('edit_appointment_time').value;
    const serviceType = document.getElementById('edit_service_type').value;
    
    if (!salonId || !hairdresserId || !date || !time || !serviceType) {
        alert('Por favor, preencha todos os campos obrigatorios!');
        return false;
    }
    
    // Valida se a data nao e no passado
    const selectedDate = new Date(date + 'T' + time);
    const now = new Date();
    
    if (selectedDate < now) {
        alert('A data e hora do agendamento nao podem ser no passado!');
        return false;
    }
    
    return true;
}

// Cancelar agendamento
function cancelAppointment(id) {
    if (confirm('Tem certeza que deseja cancelar este agendamento?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/cancel_appointment/${id}`;
        document.body.appendChild(form);
        form.submit();
    }
}

// Excluir agendamento
function deleteAppointment(id) {
    if (confirm('Tem certeza que deseja excluir este agendamento? Esta acao nao pode ser desfeita!')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/delete_appointment/${id}`;
        document.body.appendChild(form);
        form.submit();
    }
}
