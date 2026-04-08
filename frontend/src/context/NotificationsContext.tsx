import { createContext, useContext, useEffect, useState } from "react";
import { getUnreadCount } from "../api/notificaciones";
import { useAuth } from "./AuthContext";

type NotificationsContextType = {
    unreadCount: number;
    reloadUnreadCount: () => Promise<void>;
};

const NotificationsContext = createContext<NotificationsContextType | undefined>(
    undefined
);

export const NotificationsProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const { user } = useAuth();
    const [unreadCount, setUnreadCount] = useState(0);

    const reloadUnreadCount = async () => {
        if (!user) {
            setUnreadCount(0);
            return;
        }

        try {
            const count = await getUnreadCount();
            setUnreadCount(count);
        } catch (error) {
            console.error("Error obteniendo notificaciones:", error);
        }
    };


    useEffect(() => {
        if (!user?.id) {
            setUnreadCount(0);
            return;
        }

        reloadUnreadCount();

        const handleUpdate = () => {
            reloadUnreadCount();
        };

        window.addEventListener("notificaciones-actualizadas", handleUpdate);

        return () => {
            window.removeEventListener("notificaciones-actualizadas", handleUpdate);
        };
    }, [user?.id]);


    return (
        <NotificationsContext.Provider
            value={{
                unreadCount,
                reloadUnreadCount,
            }}
        >
            {children}
        </NotificationsContext.Provider>
    );
};

export const useNotifications = () => {
    const ctx = useContext(NotificationsContext);
    if (!ctx) {
        throw new Error(
            "useNotifications debe usarse dentro de NotificationsProvider"
        );
    }
    return ctx;
};