const Modal = ({ show, onClose, title, children }) => {
  if (!show) return null;
  
  return (
    <div 
      style={{
        position: "fixed",
        zIndex: 9999,
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        overflowY: "auto"  /* ✅ ADDED: Allow background scroll */
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: "#fff",
          borderRadius: 16,
          boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
          padding: 0,  /* ✅ CHANGED: Remove padding from container */
          maxWidth: 600,  /* ✅ INCREASED: From 500px to 600px for more space */
          width: "100%",
          position: "relative",
          margin: "auto",  /* ✅ ADDED: Center in viewport */
          maxHeight: "90vh",  /* ✅ ADDED: Limit to 90% of viewport height */
          display: "flex",  /* ✅ ADDED: Flexbox layout */
          flexDirection: "column"  /* ✅ ADDED: Stack vertically */
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Fixed Header */}
        <div style={{
          padding: "24px 32px",
          borderBottom: "2px solid #e2e8f0",
          flexShrink: 0  /* ✅ ADDED: Don't shrink header */
        }}>
          <h2 style={{ 
            margin: 0,
            fontSize: 22,
            fontWeight: 700,
            color: '#1f2937',
            paddingRight: "32px"  /* ✅ ADDED: Space for close button */
          }}>
            {title}
          </h2>

          {/* Close X Button - Positioned in Header */}
          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: 20,
              right: 20,
              background: '#f3f4f6',
              border: 'none',
              fontSize: 24,
              fontWeight: 700,
              color: '#6b7280',
              cursor: 'pointer',
              lineHeight: 1,
              padding: 0,
              width: 36,
              height: 36,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.background = '#e5e7eb';
              e.target.style.color = '#374151';
            }}
            onMouseOut={(e) => {
              e.target.style.background = '#f3f4f6';
              e.target.style.color = '#6b7280';
            }}
          >
            ×
          </button>
        </div>

        {/* Scrollable Content Area */}
        <div style={{
          padding: "24px 32px",
          overflowY: "auto",  /* ✅ ADDED: Make content scrollable */
          flex: 1,  /* ✅ ADDED: Take remaining space */
          minHeight: 0  /* ✅ ADDED: Allow flex shrinking */
        }}>
          {children}
        </div>

        {/* Fixed Footer with OK Button */}
        <div style={{
          padding: "16px 32px 24px",
          borderTop: "1px solid #e2e8f0",
          flexShrink: 0  /* ✅ ADDED: Don't shrink footer */
        }}>
          <button
            style={{
              background: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "12px 32px",
              fontWeight: 600,
              cursor: "pointer",
              width: "100%",
              fontSize: 16,
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
              transition: "all 0.2s ease"
            }}
            onClick={onClose}
            onMouseOver={(e) => {
              e.target.style.transform = "translateY(-2px)";
              e.target.style.boxShadow = "0 6px 16px rgba(59, 130, 246, 0.4)";
            }}
            onMouseOut={(e) => {
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = "0 4px 12px rgba(59, 130, 246, 0.3)";
            }}
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};



export default Modal;
