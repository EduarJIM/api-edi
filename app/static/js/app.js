/**
 * TASK STUDIO - API EDI FRONTEND CLIENT
 * 100% Focused on Task Management: Add, Update, Delete, Suspend, Check completion & Live Search.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        tasks: [],
        activeTab: 'tab-tasks'
    };

    // DOM Elements
    const elements = {
        // KPI Metrics
        kpiTotalTasks: document.getElementById('kpiTotalTasks'),
        kpiPendingTasks: document.getElementById('kpiPendingTasks'),
        kpiProgressTasks: document.getElementById('kpiProgressTasks'),
        kpiSuspendedTasks: document.getElementById('kpiSuspendedTasks'),
        kpiCompletedTasks: document.getElementById('kpiCompletedTasks'),

        // Header & Status
        renderStatusText: document.getElementById('renderStatusText'),

        // Task Filters & Actions
        tasksList: document.getElementById('tasksList'),
        tasksLoading: document.getElementById('tasksLoading'),
        tasksEmpty: document.getElementById('tasksEmpty'),
        taskSearchInput: document.getElementById('taskSearchInput'),
        taskStatusFilter: document.getElementById('taskStatusFilter'),
        taskPriorityFilter: document.getElementById('taskPriorityFilter'),
        btnRefreshTasks: document.getElementById('btnRefreshTasks'),

        // Modals
        modalNewTask: document.getElementById('modalNewTask'),
        modalEditTask: document.getElementById('modalEditTask'),
        btnOpenNewTaskModal: document.getElementById('btnOpenNewTaskModal'),

        // Forms
        formNewTask: document.getElementById('formNewTask'),
        formEditTask: document.getElementById('formEditTask'),

        // Render Monitor
        btnPingHealth: document.getElementById('btnPingHealth'),
        healthStatusMsg: document.getElementById('healthStatusMsg'),
        healthResponseCode: document.getElementById('healthResponseCode'),
        renderHealthCard: document.getElementById('renderHealthCard'),

        // Query Console
        queryMethod: document.getElementById('queryMethod'),
        queryUrl: document.getElementById('queryUrl'),
        btnExecuteQuery: document.getElementById('btnExecuteQuery'),
        queryBodyContainer: document.getElementById('queryBodyContainer'),
        queryRequestBody: document.getElementById('queryRequestBody'),
        queryStatusCode: document.getElementById('queryStatusCode'),
        queryResponseTime: document.getElementById('queryResponseTime'),
        queryResponseBody: document.getElementById('queryResponseBody'),

        // Toast Container
        toastContainer: document.getElementById('toastContainer')
    };

    // Initialize Application
    init();

    async function init() {
        setupTabs();
        setupEventListeners();
        await fetchTasks();
        checkRenderHealth();
    }

    // Tabs Navigation
    function setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-tab');
                tabBtns.forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

                btn.classList.add('active');
                document.getElementById(targetTab).classList.add('active');
                state.activeTab = targetTab;
            });
        });
    }

    // Event Listeners
    function setupEventListeners() {
        // Filters & Search
        elements.taskSearchInput.addEventListener('input', filterAndRenderTasks);
        elements.taskStatusFilter.addEventListener('change', filterAndRenderTasks);
        elements.taskPriorityFilter.addEventListener('change', filterAndRenderTasks);
        elements.btnRefreshTasks.addEventListener('click', fetchTasks);

        // Keyboard Shortcut: '/' focuses search input
        window.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                elements.taskSearchInput.focus();
            }
        });

        // Render Health Ping
        elements.btnPingHealth.addEventListener('click', checkRenderHealth);

        // Modals Open & Close
        elements.btnOpenNewTaskModal.addEventListener('click', () => openModal(elements.modalNewTask));
        document.getElementById('btnCloseTaskModal').addEventListener('click', () => closeModal(elements.modalNewTask));
        document.getElementById('btnCancelTaskModal').addEventListener('click', () => closeModal(elements.modalNewTask));

        document.getElementById('btnCloseEditTaskModal').addEventListener('click', () => closeModal(elements.modalEditTask));
        document.getElementById('btnCancelEditTaskModal').addEventListener('click', () => closeModal(elements.modalEditTask));

        // Form Submissions
        elements.formNewTask.addEventListener('submit', handleCreateTask);
        elements.formEditTask.addEventListener('submit', handleEditTask);

        // Query Console Method Selector
        elements.queryMethod.addEventListener('change', (e) => {
            const method = e.target.value;
            if (method === 'POST' || method === 'PUT') {
                elements.queryBodyContainer.classList.remove('hidden');
            } else {
                elements.queryBodyContainer.classList.add('hidden');
            }
        });

        elements.btnExecuteQuery.addEventListener('click', executeCustomQuery);
    }

    // Fetch Tasks from API
    async function fetchTasks() {
        elements.tasksLoading.classList.remove('hidden');
        elements.tasksEmpty.classList.add('hidden');
        elements.tasksList.innerHTML = '';

        try {
            const res = await fetch('/api/tareas');
            if (!res.ok) throw new Error('Error al obtener lista de tareas');
            state.tasks = await res.json();

            // If zero tasks exist on fresh start, seed sample demo tasks automatically
            if (state.tasks.length === 0) {
                await seedSampleTasks();
                return;
            }

            updateKPIs();
            filterAndRenderTasks();
            showToast('Tareas sincronizadas con la base de datos', 'info');
        } catch (err) {
            console.error('Error al cargar tareas:', err);
            showToast('Error de conexión con la API: ' + err.message, 'error');
        } finally {
            elements.tasksLoading.classList.add('hidden');
        }
    }

    // Seed Demo Tasks if Database is Empty
    async function seedSampleTasks() {
        const samples = [
            { codigo: 'EDI-850', titulo: 'Procesar Orden de Compra EDI', descripcion: 'Mapear campos XML a base de datos de pedidos EDI', prioridad: 'alta', estado: 'en_progreso' },
            { codigo: 'TAR-002', titulo: 'Sincronizar inventario con Render', descripcion: 'Verificar Webhooks de despliegue en ambiente cloud', prioridad: 'media', estado: 'pendiente' },
            { codigo: 'TAR-003', titulo: 'Mantenimiento de servidor de base de datos', descripcion: 'Limpieza de logs y respaldo automatizado', prioridad: 'critica', estado: 'suspendido' },
            { codigo: 'TAR-004', titulo: 'Verificación de endpoints REST', descripcion: 'Ejecutar suite de pruebas de integración', prioridad: 'baja', estado: 'completado' }
        ];

        for (const sample of samples) {
            await fetch('/api/tareas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sample)
            });
        }

        const res = await fetch('/api/tareas');
        state.tasks = await res.json();
        updateKPIs();
        filterAndRenderTasks();
    }

    // Filter & Render Tasks Grid
    function filterAndRenderTasks() {
        const search = elements.taskSearchInput.value.toLowerCase().trim();
        const statusFilter = elements.taskStatusFilter.value;
        const priorityFilter = elements.taskPriorityFilter.value;

        const filtered = state.tasks.filter(task => {
            const matchesSearch = !search || 
                (task.codigo && task.codigo.toLowerCase().includes(search)) ||
                (task.titulo && task.titulo.toLowerCase().includes(search)) ||
                (task.descripcion && task.descripcion.toLowerCase().includes(search));
            
            const matchesStatus = !statusFilter || task.estado === statusFilter;
            const matchesPriority = !priorityFilter || task.prioridad === priorityFilter;

            return matchesSearch && matchesStatus && matchesPriority;
        });

        if (filtered.length === 0) {
            elements.tasksEmpty.classList.remove('hidden');
            elements.tasksList.innerHTML = '';
            return;
        }

        elements.tasksEmpty.classList.add('hidden');
        elements.tasksList.innerHTML = filtered.map(task => createTaskCardHTML(task)).join('');

        // Attach Event Listeners to Card Buttons
        filtered.forEach(task => {
            // Check button
            const checkBtn = document.getElementById(`check-btn-${task.id}`);
            if (checkBtn) {
                checkBtn.addEventListener('click', () => toggleTaskCheck(task));
            }

            // Suspend button
            const suspendBtn = document.getElementById(`suspend-btn-${task.id}`);
            if (suspendBtn) {
                suspendBtn.addEventListener('click', () => toggleTaskSuspend(task));
            }

            // Edit button
            const editBtn = document.getElementById(`edit-btn-${task.id}`);
            if (editBtn) {
                editBtn.addEventListener('click', () => openEditTaskModal(task));
            }

            // Delete button
            const deleteBtn = document.getElementById(`delete-btn-${task.id}`);
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => deleteTask(task.id, task.codigo));
            }
        });
    }

    // HTML Generator for Task Card
    function createTaskCardHTML(task) {
        const isCompleted = task.estado === 'completado';
        const isSuspended = task.estado === 'suspendido';
        const createdDate = task.creado_en ? new Date(task.creado_en).toLocaleString('es-ES') : 'Reciente';

        let statusText = 'Pendiente ⏳';
        if (task.estado === 'en_progreso') statusText = 'En Progreso ⚙️';
        if (task.estado === 'suspendido') statusText = 'Suspendida ⏸️';
        if (task.estado === 'completado') statusText = 'Completada ✅';

        return `
            <div class="task-card" id="task-card-${task.id}">
                <div class="task-card-header">
                    <div class="task-info-group">
                        <button class="btn-check ${isCompleted ? 'checked' : ''}" 
                                id="check-btn-${task.id}" 
                                title="${isCompleted ? 'Marcar como pendiente' : 'Marcar como completada (Check)'}">
                            <i class="fa-solid fa-check"></i>
                        </button>
                        <div>
                            <span class="task-code-badge">${escapeHtml(task.codigo)}</span>
                            <h3 class="task-title">${escapeHtml(task.titulo)}</h3>
                        </div>
                    </div>
                    <span class="badge-priority priority-${task.prioridad}">${task.prioridad}</span>
                </div>

                ${task.descripcion ? `
                    <div class="task-description">
                        <i class="fa-solid fa-quote-left"></i> ${escapeHtml(task.descripcion)}
                    </div>
                ` : ''}

                <div class="task-card-footer">
                    <span class="badge-status status-${task.estado}">${statusText}</span>
                    
                    <div class="task-actions">
                        <button class="btn btn-suspend btn-sm" id="suspend-btn-${task.id}" title="${isSuspended ? 'Reanudar Tarea' : 'Suspender Tarea'}">
                            <i class="fa-solid ${isSuspended ? 'fa-play' : 'fa-pause'}"></i> ${isSuspended ? 'Reanudar' : 'Suspender'}
                        </button>
                        <button class="btn btn-edit btn-sm" id="edit-btn-${task.id}" title="Editar Tarea">
                            <i class="fa-solid fa-pen"></i> Editar
                        </button>
                        <button class="btn btn-danger btn-sm" id="delete-btn-${task.id}" title="Eliminar Tarea">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // Toggle Task Check (Completed vs Pending)
    async function toggleTaskCheck(task) {
        const newStatus = task.estado === 'completado' ? 'pendiente' : 'completado';
        await updateTaskStatus(task.id, newStatus, newStatus === 'completado' ? `✅ Tarea ${task.codigo} marcada como COMPLETADA` : `⏳ Tarea ${task.codigo} marcada como PENDIENTE`);
    }

    // Toggle Task Suspend (Suspend vs Resume)
    async function toggleTaskSuspend(task) {
        try {
            const res = await fetch(`/api/tareas/${task.id}/suspender`, { method: 'PUT' });
            if (!res.ok) throw new Error('Error al suspender la tarea');
            const data = await res.json();

            // Update local state
            const index = state.tasks.findIndex(t => t.id === task.id);
            if (index !== -1) state.tasks[index] = data.tarea;

            updateKPIs();
            filterAndRenderTasks();
            showToast(data.mensaje, 'info');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Common status update helper
    async function updateTaskStatus(taskId, status, successMsg) {
        try {
            const res = await fetch(`/api/tareas/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estado: status })
            });

            if (!res.ok) throw new Error('Error al actualizar estado de la tarea');
            const updatedTask = await res.json();

            const index = state.tasks.findIndex(t => t.id === taskId);
            if (index !== -1) state.tasks[index] = updatedTask;

            updateKPIs();
            filterAndRenderTasks();
            showToast(successMsg, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Delete Task
    async function deleteTask(taskId, codigo) {
        if (!confirm(`¿Estás seguro de que deseas eliminar la tarea ${codigo}?`)) return;

        try {
            const res = await fetch(`/api/tareas/${taskId}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Error al eliminar la tarea');

            state.tasks = state.tasks.filter(t => t.id !== taskId);
            updateKPIs();
            filterAndRenderTasks();
            showToast(`🗑️ Tarea ${codigo} eliminada correctamente`, 'info');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Open Edit Task Modal
    function openEditTaskModal(task) {
        document.getElementById('editTaskId').value = task.id;
        document.getElementById('editTaskNumberEdi').value = task.codigo;
        document.getElementById('editTaskTitulo').value = task.titulo;
        document.getElementById('editTaskObservaciones').value = task.descripcion || '';
        document.getElementById('editTaskPrioridad').value = task.prioridad;
        document.getElementById('editTaskEstado').value = task.estado;

        openModal(elements.modalEditTask);
    }

    // Create Task Submission
    async function handleCreateTask(e) {
        e.preventDefault();
        const payload = {
            codigo: document.getElementById('taskNumberEdi').value.trim(),
            titulo: document.getElementById('taskTitulo').value.trim(),
            descripcion: document.getElementById('taskObservaciones').value.trim(),
            prioridad: document.getElementById('taskPrioridad').value,
            estado: document.getElementById('taskEstado').value
        };

        try {
            const res = await fetch('/api/tareas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Error al agregar la tarea');

            closeModal(elements.modalNewTask);
            elements.formNewTask.reset();
            showToast(`✨ Tarea '${payload.codigo}' agregada correctamente`, 'success');
            await fetchTasks();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Edit Task Submission
    async function handleEditTask(e) {
        e.preventDefault();
        const taskId = document.getElementById('editTaskId').value;
        const payload = {
            codigo: document.getElementById('editTaskNumberEdi').value.trim(),
            titulo: document.getElementById('editTaskTitulo').value.trim(),
            descripcion: document.getElementById('editTaskObservaciones').value.trim(),
            prioridad: document.getElementById('editTaskPrioridad').value,
            estado: document.getElementById('editTaskEstado').value
        };

        try {
            const res = await fetch(`/api/tareas/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const updatedTask = await res.json();
            if (!res.ok) throw new Error(updatedTask.error || 'Error al actualizar la tarea');

            closeModal(elements.modalEditTask);
            showToast(`📝 Tarea '${payload.codigo}' actualizada con éxito`, 'success');

            const index = state.tasks.findIndex(t => t.id == taskId);
            if (index !== -1) state.tasks[index] = updatedTask;

            updateKPIs();
            filterAndRenderTasks();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Update KPI Metric Cards
    function updateKPIs() {
        elements.kpiTotalTasks.textContent = state.tasks.length;
        elements.kpiPendingTasks.textContent = state.tasks.filter(t => t.estado === 'pendiente').length;
        elements.kpiProgressTasks.textContent = state.tasks.filter(t => t.estado === 'en_progreso').length;
        elements.kpiSuspendedTasks.textContent = state.tasks.filter(t => t.estado === 'suspendido').length;
        elements.kpiCompletedTasks.textContent = state.tasks.filter(t => t.estado === 'completado').length;
    }

    // Render Health Check
    async function checkRenderHealth() {
        const startTime = performance.now();
        elements.healthStatusMsg.textContent = 'Contactando con Render en /api/health...';

        try {
            const res = await fetch('/api/health');
            const endTime = performance.now();
            const latency = Math.round(endTime - startTime);
            const data = await res.json();

            elements.healthResponseCode.textContent = JSON.stringify(data, null, 2);

            if (res.ok && data.status === 'healthy') {
                elements.renderStatusText.textContent = `Render: Online (${latency} ms)`;
                elements.healthStatusMsg.innerHTML = `<i class="fa-solid fa-circle-check"></i> Servicio Render Operativo • Latencia: <strong>${latency} ms</strong>`;
                elements.renderHealthCard.className = 'render-health-results status-healthy';
            } else {
                elements.renderStatusText.textContent = 'Render: Degradado';
                elements.healthStatusMsg.textContent = 'Respuesta no saludable del servidor';
            }
        } catch (err) {
            elements.renderStatusText.textContent = 'Render: Offline';
            elements.healthStatusMsg.textContent = 'No se pudo contactar con el endpoint de salud';
            elements.healthResponseCode.textContent = JSON.stringify({ error: err.message }, null, 2);
        }
    }

    // Custom API Query Console
    async function executeCustomQuery() {
        const method = elements.queryMethod.value;
        const url = elements.queryUrl.value.trim();
        const startTime = performance.now();

        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };

        if ((method === 'POST' || method === 'PUT') && elements.queryRequestBody.value) {
            try {
                options.body = JSON.stringify(JSON.parse(elements.queryRequestBody.value));
            } catch (err) {
                showToast('JSON de petición no válido', 'error');
                return;
            }
        }

        try {
            const res = await fetch(url, options);
            const endTime = performance.now();
            const latency = Math.round(endTime - startTime);

            elements.queryStatusCode.textContent = `${res.status} ${res.statusText}`;
            elements.queryStatusCode.className = `badge-status ${res.ok ? 'status-completado' : 'status-suspendido'}`;
            elements.queryResponseTime.textContent = `${latency} ms`;

            const data = await res.json();
            elements.queryResponseBody.textContent = JSON.stringify(data, null, 2);
        } catch (err) {
            elements.queryStatusCode.textContent = 'ERROR';
            elements.queryStatusCode.className = 'badge-status status-suspendido';
            elements.queryResponseBody.textContent = JSON.stringify({ error: err.message }, null, 2);
        }
    }

    // Modal Helpers
    function openModal(modal) { modal.classList.remove('hidden'); }
    function closeModal(modal) { modal.classList.add('hidden'); }

    // Toast Notification System
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-circle-check';
        if (type === 'error') icon = 'fa-circle-exclamation';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Escape HTML
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
