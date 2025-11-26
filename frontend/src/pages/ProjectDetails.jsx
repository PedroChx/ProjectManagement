import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService, taskService } from '../services/api';
import { 
    ArrowLeft, Trash2, Edit2, Plus, CheckCircle2, 
    Clock, Save, X, Calendar, User
} from 'lucide-react';

export default function ProjectDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    
    const [project, setProject] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // Estados UI
    const [isEditing, setIsEditing] = useState(false);
    const [showTaskModal, setShowTaskModal] = useState(false);
    const [currentTask, setCurrentTask] = useState(null);
    
    // Formulario proyecto
    const [editForm, setEditForm] = useState({ name: '', description: '', status: '' });

    useEffect(() => {
        loadData();
    }, [id]);

    const loadData = async () => {
        try {
            setLoading(true);
            const [projRes, taskRes] = await Promise.all([
                projectService.getById(id),
                taskService.getByProject(id)
            ]);
            setProject(projRes.project);
            setEditForm(projRes.project);
            setTasks(taskRes.tasks || []);
        } catch (error) {
            console.error(error);
            navigate('/dashboard');
        } finally {
            setLoading(false);
        }
    };

    const handleProjectUpdate = async (e) => {
        e.preventDefault();
        try {
            await projectService.update(id, {
                name: editForm.name,
                description: editForm.description,
                status: editForm.status
            });
            setIsEditing(false);
            loadData();
        } catch (error) {
            alert('Error al actualizar');
        }
    };

    const handleProjectDelete = async () => {
        if(confirm('¿Estás seguro de borrar este proyecto?')) {
            await projectService.delete(id);
            navigate('/dashboard');
        }
    };

    const handleTaskSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            status: formData.get('status'),
            assignedTo: project.createdBy
        };

        try {
            if (currentTask) {
                await taskService.update(id, currentTask.taskId, data);
            } else {
                await taskService.create(id, data);
            }
            setShowTaskModal(false);
            setCurrentTask(null);
            loadData();
        } catch (error) {
            console.error(error);
        }
    };

    const handleTaskDelete = async (taskId) => {
        if(confirm('¿Borrar tarea?')) {
            await taskService.delete(id, taskId);
            loadData();
        }
    };

    if (loading) return (
        <div style={styles.loadingContainer}>
            <div style={styles.spinner}></div>
        </div>
    );

    return (
        <div style={styles.container}>
            <div style={styles.wrapper}>
                
                {/* Navegación */}
                <button onClick={() => navigate('/dashboard')} style={styles.backButton}>
                    <ArrowLeft size={20} /> Volver al Dashboard
                </button>

                {/* Tarjeta de Proyecto */}
                <div style={styles.card}>
                    {isEditing ? (
                        <form onSubmit={handleProjectUpdate} style={styles.form}>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Nombre</label>
                                <input 
                                    value={editForm.name}
                                    onChange={e => setEditForm({...editForm, name: e.target.value})}
                                    style={styles.input}
                                />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Descripción</label>
                                <textarea 
                                    value={editForm.description}
                                    onChange={e => setEditForm({...editForm, description: e.target.value})}
                                    style={styles.textarea}
                                    rows="3"
                                />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Estado</label>
                                <select 
                                    value={editForm.status}
                                    onChange={e => setEditForm({...editForm, status: e.target.value})}
                                    style={styles.select}
                                >
                                    <option value="active">Activo</option>
                                    <option value="completed">Completado</option>
                                </select>
                            </div>
                            <div style={styles.buttonGroup}>
                                <button type="button" onClick={() => setIsEditing(false)} style={styles.btnCancel}>
                                    Cancelar
                                </button>
                                <button type="submit" style={styles.btnPrimary}>
                                    <Save size={18} /> Guardar
                                </button>
                            </div>
                        </form>
                    ) : (
                        <>
                            <div style={styles.projectHeader}>
                                <div>
                                    <h1 style={styles.projectTitle}>{project.name}</h1>
                                    <div style={styles.badges}>
                                        <span style={{
                                            ...styles.statusBadge,
                                            backgroundColor: project.status === 'active' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                                            color: project.status === 'active' ? '#34d399' : '#60a5fa'
                                        }}>
                                            {project.status === 'active' ? 'Activo' : 'Completado'}
                                        </span>
                                        <span style={styles.dateBadge}>
                                            <Calendar size={14} /> {new Date(project.createdAt).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                                {project.userRole === 'owner' && (
                                    <div style={styles.actions}>
                                        <button onClick={() => setIsEditing(true)} style={styles.iconBtn}>
                                            <Edit2 size={20} />
                                        </button>
                                        <button onClick={handleProjectDelete} style={{...styles.iconBtn, color: '#f87171', backgroundColor: 'rgba(239, 68, 68, 0.1)'}}>
                                            <Trash2 size={20} />
                                        </button>
                                    </div>
                                )}
                            </div>
                            <p style={styles.description}>{project.description || 'Sin descripción'}</p>
                        </>
                    )}
                </div>

                {/* Header de Tareas */}
                <div style={styles.sectionHeader}>
                    <h2 style={styles.sectionTitle}>
                        <CheckCircle2 size={24} color="#8b5cf6" /> Tareas del Proyecto
                    </h2>
                    <button onClick={() => { setCurrentTask(null); setShowTaskModal(true); }} style={styles.btnPrimary}>
                        <Plus size={20} /> Nueva Tarea
                    </button>
                </div>

                {/* Lista de Tareas */}
                {tasks.length === 0 ? (
                    <div style={styles.emptyState}>
                        <p>No hay tareas registradas.</p>
                    </div>
                ) : (
                    <div style={styles.taskGrid}>
                        {tasks.map(task => (
                            <div key={task.taskId} style={styles.taskCard}>
                                <div style={styles.taskHeader}>
                                    <h3 style={styles.taskTitle}>{task.title}</h3>
                                    <div style={styles.taskActions}>
                                        <button onClick={() => { setCurrentTask(task); setShowTaskModal(true); }} style={styles.taskBtn}>
                                            <Edit2 size={16} />
                                        </button>
                                        <button onClick={() => handleTaskDelete(task.taskId)} style={{...styles.taskBtn, color: '#f87171'}}>
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </div>
                                <p style={styles.taskDesc}>{task.description}</p>
                                <div style={styles.taskFooter}>
                                    <span style={{
                                        ...styles.taskStatus,
                                        color: task.status === 'completed' ? '#34d399' : task.status === 'in_progress' ? '#60a5fa' : '#9ca3af'
                                    }}>
                                        {task.status === 'pending' ? 'Pendiente' : task.status === 'in_progress' ? 'En Progreso' : 'Completada'}
                                    </span>
                                    <User size={16} color="#6b7280" />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Modal Tarea */}
            {showTaskModal && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modal}>
                        <div style={styles.modalHeader}>
                            <h3 style={styles.modalTitle}>{currentTask ? 'Editar Tarea' : 'Nueva Tarea'}</h3>
                            <button onClick={() => setShowTaskModal(false)} style={styles.closeBtn}><X size={24} /></button>
                        </div>
                        <form onSubmit={handleTaskSubmit} style={styles.form}>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Título</label>
                                <input name="title" defaultValue={currentTask?.title} required style={styles.input} />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Descripción</label>
                                <textarea name="description" defaultValue={currentTask?.description} rows="3" style={styles.textarea} />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Estado</label>
                                <select name="status" defaultValue={currentTask?.status || 'pending'} style={styles.select}>
                                    <option value="pending">Pendiente</option>
                                    <option value="in_progress">En Progreso</option>
                                    <option value="completed">Completada</option>
                                </select>
                            </div>
                            <button type="submit" style={styles.btnPrimary}>Guardar</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

const styles = {
    container: {
        minHeight: '100vh',
        backgroundColor: '#030712',
        color: '#fff',
        padding: '24px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
    },
    loadingContainer: {
        minHeight: '100vh',
        backgroundColor: '#030712',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    },
    spinner: {
        width: '40px',
        height: '40px',
        border: '4px solid #374151',
        borderTop: '4px solid #8b5cf6',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
    },
    wrapper: {
        maxWidth: '1024px',
        margin: '0 auto',
    },
    backButton: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: 'none',
        border: 'none',
        color: '#9ca3af',
        cursor: 'pointer',
        marginBottom: '24px',
        fontSize: '14px',
    },
    card: {
        backgroundColor: '#111827',
        border: '1px solid #1f2937',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '32px',
    },
    projectHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px',
    },
    projectTitle: {
        fontSize: '30px',
        fontWeight: 'bold',
        margin: '0 0 12px 0',
    },
    badges: {
        display: 'flex',
        gap: '12px',
        alignItems: 'center',
    },
    statusBadge: {
        padding: '4px 12px',
        borderRadius: '999px',
        fontSize: '12px',
        fontWeight: '600',
    },
    dateBadge: {
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        color: '#9ca3af',
        fontSize: '13px',
    },
    actions: {
        display: 'flex',
        gap: '8px',
    },
    iconBtn: {
        padding: '8px',
        backgroundColor: '#1f2937',
        border: 'none',
        borderRadius: '8px',
        color: '#e5e7eb',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    description: {
        color: '#9ca3af',
        lineHeight: '1.5',
    },
    sectionHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
    },
    sectionTitle: {
        fontSize: '24px',
        fontWeight: 'bold',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        margin: 0,
    },
    btnPrimary: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        backgroundColor: '#8b5cf6',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        borderRadius: '8px',
        fontWeight: '600',
        cursor: 'pointer',
        justifyContent: 'center',
    },
    btnCancel: {
        backgroundColor: '#374151',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        borderRadius: '8px',
        fontWeight: '600',
        cursor: 'pointer',
    },
    taskGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '16px',
    },
    taskCard: {
        backgroundColor: '#111827',
        border: '1px solid #1f2937',
        borderRadius: '8px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
    },
    taskHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '8px',
    },
    taskTitle: {
        fontWeight: '600',
        fontSize: '16px',
        color: '#e5e7eb',
        margin: 0,
    },
    taskActions: {
        display: 'flex',
        gap: '4px',
    },
    taskBtn: {
        background: 'none',
        border: 'none',
        color: '#9ca3af',
        cursor: 'pointer',
        padding: '4px',
    },
    taskDesc: {
        color: '#9ca3af',
        fontSize: '14px',
        marginBottom: '16px',
        flex: 1,
    },
    taskFooter: {
        borderTop: '1px solid #374151',
        paddingTop: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    taskStatus: {
        fontSize: '12px',
        fontWeight: '500',
    },
    emptyState: {
        textAlign: 'center',
        padding: '48px',
        backgroundColor: 'rgba(17, 24, 39, 0.5)',
        border: '1px dashed #374151',
        borderRadius: '12px',
        color: '#6b7280',
    },
    modalOverlay: {
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.75)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)',
    },
    modal: {
        backgroundColor: '#111827',
        border: '1px solid #1f2937',
        borderRadius: '12px',
        padding: '24px',
        width: '100%',
        maxWidth: '480px',
    },
    modalHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
    },
    modalTitle: {
        fontSize: '20px',
        fontWeight: 'bold',
        margin: 0,
    },
    closeBtn: {
        background: 'none',
        border: 'none',
        color: '#9ca3af',
        cursor: 'pointer',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
    },
    formGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    },
    label: {
        fontSize: '14px',
        color: '#d1d5db',
        fontWeight: '500',
    },
    input: {
        backgroundColor: '#1f2937',
        border: '1px solid #374151',
        borderRadius: '8px',
        padding: '10px',
        color: 'white',
        outline: 'none',
    },
    textarea: {
        backgroundColor: '#1f2937',
        border: '1px solid #374151',
        borderRadius: '8px',
        padding: '10px',
        color: 'white',
        outline: 'none',
        fontFamily: 'inherit',
        resize: 'vertical',
    },
    select: {
        backgroundColor: '#1f2937',
        border: '1px solid #374151',
        borderRadius: '8px',
        padding: '10px',
        color: 'white',
        outline: 'none',
    },
    buttonGroup: {
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '12px',
        marginTop: '8px',
    }
};