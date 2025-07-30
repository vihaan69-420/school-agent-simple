import { create } from 'zustand';

const generateId = () => Math.random().toString(36).substr(2, 9);

export const useChatStore = create((set, get) => ({
      // Theme state
      isDarkMode: false,
      toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),

      // Chat sessions
      sessions: [],
      currentSessionId: null,
      sidebarOpen: false,

      // Actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      createNewSession: () => {
        const id = generateId();
        const newSession = {
          id,
          title: 'New Chat',
          messages: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        
        set((state) => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: id
        }));
        
        return id;
      },

      switchSession: (sessionId) => {
        set({ currentSessionId: sessionId });
      },

      deleteSession: (sessionId) => {
        set((state) => {
          const newSessions = state.sessions.filter(s => s.id !== sessionId);
          const newCurrentId = state.currentSessionId === sessionId 
            ? (newSessions.length > 0 ? newSessions[0].id : null)
            : state.currentSessionId;
          
          return {
            sessions: newSessions,
            currentSessionId: newCurrentId
          };
        });
      },

      renameSession: (sessionId, newTitle) => {
        set((state) => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? { ...session, title: newTitle, updatedAt: new Date().toISOString() }
              : session
          )
        }));
      },

      addMessage: (sessionId, message) => {
        set((state) => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: [...session.messages, { ...message, id: generateId() }],
                  updatedAt: new Date().toISOString()
                }
              : session
          )
        }));
      },

      updateMessage: (sessionId, messageId, updates) => {
        set((state) => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.map(msg =>
                    msg.id === messageId ? { ...msg, ...updates } : msg
                  ),
                  updatedAt: new Date().toISOString()
                }
              : session
          )
        }));
      },

      getCurrentSession: () => {
        const { sessions, currentSessionId } = get();
        return sessions.find(s => s.id === currentSessionId) || null;
      },

      // Input state
      inputValue: '',
      setInputValue: (value) => set({ inputValue: value }),
      
      // Loading state
      isLoading: false,
      setIsLoading: (loading) => set({ isLoading: loading }),
}));