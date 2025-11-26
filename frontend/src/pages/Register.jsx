import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, AlertCircle, Folder } from 'lucide-react';

export default function Register() {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
    };

    const validateForm = () => {
        if (formData.name.length < 3) {
            setError('El nombre debe tener al menos 3 caracteres');
            return false;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            setError('Email inválido');
            return false;
        }
        if (formData.password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return false;
        }
        if (formData.password !== formData.confirmPassword) {
            setError('Las contraseñas no coinciden');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        setError('');

        const { confirmPassword, ...registerData } = formData;
        const result = await register(registerData);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }
        setLoading(false);
    };

    return (
        <div style={styles.container}>
            <div style={styles.content}>
                {/* Header Logo */}
                <div style={styles.header}>
                    <div style={styles.logoBox}>
                        <UserPlus size={32} color="white" />
                    </div>
                    <h1 style={styles.title}>ProjectHub</h1>
                    <p style={styles.subtitle}>Gestión de Proyectos</p>
                </div>

                {/* Card */}
                <div style={styles.card}>
                    <h2 style={styles.cardTitle}>Crear Cuenta</h2>

                    {error && (
                        <div style={styles.errorContainer}>
                            <AlertCircle size={20} color="#ef4444" />
                            <p style={styles.errorText}>{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} style={styles.form}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Nombre Completo</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                                style={styles.input}
                                placeholder="Ej: Pedro López"
                            />
                        </div>

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Email</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                                style={styles.input}
                                placeholder="tu@email.com"
                            />
                        </div>

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Contraseña</label>
                            <input
                                type="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                style={styles.input}
                                placeholder="Mínimo 6 caracteres"
                            />
                        </div>

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Confirmar Contraseña</label>
                            <input
                                type="password"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                required
                                style={styles.input}
                                placeholder="Repite la contraseña"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            style={{
                                ...styles.button,
                                opacity: loading ? 0.7 : 1,
                                cursor: loading ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {loading ? 'Creando cuenta...' : 'Crear Cuenta'}
                        </button>
                    </form>

                    <div style={styles.footer}>
                        <p style={styles.footerText}>
                            ¿Ya tienes cuenta?{' '}
                            <Link to="/login" style={styles.link}>
                                Iniciar sesión
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

const styles = {
    container: {
        minHeight: '100vh',
        backgroundColor: '#030712',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
    },
    content: {
        width: '100%',
        maxWidth: '450px',
    },
    header: {
        textAlign: 'center',
        marginBottom: '32px',
    },
    logoBox: {
        width: '64px',
        height: '64px',
        backgroundColor: '#8b5cf6',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 16px',
    },
    title: {
        fontSize: '28px',
        fontWeight: 'bold',
        color: '#fff',
        margin: '0 0 8px 0',
    },
    subtitle: {
        color: '#9ca3af',
        margin: 0,
        fontSize: '14px',
    },
    card: {
        backgroundColor: '#111827',
        border: '1px solid #1f2937',
        borderRadius: '12px',
        padding: '32px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    },
    cardTitle: {
        color: '#fff',
        fontSize: '24px',
        fontWeight: 'bold',
        marginBottom: '24px',
        margin: '0 0 24px 0',
    },
    errorContainer: {
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid rgba(239, 68, 68, 0.2)',
        borderRadius: '8px',
        padding: '12px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    errorText: {
        color: '#f87171',
        fontSize: '14px',
        margin: 0,
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
    },
    formGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    },
    label: {
        color: '#d1d5db',
        fontSize: '14px',
        fontWeight: '500',
    },
    input: {
        backgroundColor: '#1f2937',
        border: '1px solid #374151',
        borderRadius: '8px',
        padding: '12px 16px',
        color: '#fff',
        fontSize: '14px',
        outline: 'none',
        transition: 'border-color 0.2s',
    },
    button: {
        backgroundColor: '#8b5cf6',
        color: '#fff',
        border: 'none',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '16px',
        fontWeight: '600',
        cursor: 'pointer',
        marginTop: '8px',
        transition: 'background-color 0.2s',
    },
    footer: {
        marginTop: '24px',
        textAlign: 'center',
    },
    footerText: {
        color: '#9ca3af',
        fontSize: '14px',
        margin: 0,
    },
    link: {
        color: '#a78bfa',
        textDecoration: 'none',
        fontWeight: '600',
    }
};