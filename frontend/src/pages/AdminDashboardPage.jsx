/**
 * Administrator Portal Dashboard (/admin/dashboard)
 * Provides platform metrics, pharmacy verification workflows,
 * medicine catalogue management, user roster, and audit logging.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from '../context/RouterContext';
import { portalService } from '../services/portalService';

export default function AdminDashboardPage() {
  const { user, logout } = useAuth();
  const { navigate } = useRouter();

  const [activeTab, setActiveTab] = useState('verifications'); // 'verifications' | 'catalogue' | 'users' | 'audit'
  const [overview, setOverview] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Pharmacy Verification State
  const [pharmacies, setPharmacies] = useState([]);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [rejectingPharmacy, setRejectingPharmacy] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [isProcessingAction, setIsProcessingAction] = useState(false);

  // Catalogue Management State
  const [medicines, setMedicines] = useState([]);
  const [medSearch, setMedSearch] = useState('');
  const [showAddMedModal, setShowAddMedModal] = useState(false);
  const [newMedData, setNewMedData] = useState({
    generic_name: '',
    brand_name: '',
    strength: '',
    dosage_form: 'Tablet',
    pack_size: 'Strip of 10',
    search_aliases: '',
  });

  // Users State
  const [users, setUsers] = useState([]);

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState([]);

  // Load Overview Counts
  const loadOverview = useCallback(async () => {
    try {
      const data = await portalService.getAdminOverview();
      setOverview(data);
    } catch (err) {
      console.error('Failed to load admin overview:', err);
    }
  }, []);

  // Load Tab-specific Data
  const loadTabData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'verifications') {
        const data = await portalService.getAdminPharmacies(statusFilter);
        setPharmacies(data || []);
      } else if (activeTab === 'catalogue') {
        const data = await portalService.getAdminMedicines(medSearch);
        setMedicines(data || []);
      } else if (activeTab === 'users') {
        const data = await portalService.getAdminUsers();
        setUsers(data || []);
      } else if (activeTab === 'audit') {
        const data = await portalService.getAdminAuditLogs();
        setAuditLogs(data || []);
      }
    } catch (err) {
      console.error('Error fetching admin tab data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, statusFilter, medSearch]);

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    loadTabData();
  }, [loadTabData]);

  // Pharmacy Verification Actions
  const handleApprovePharmacy = async (pharmacyId, pharmacyName) => {
    if (!window.confirm(`Approve and verify "${pharmacyName}"? This will activate their inventory on the live search network.`)) {
      return;
    }
    setIsProcessingAction(true);
    try {
      await portalService.verifyAdminPharmacy(pharmacyId, 'approve');
      await loadOverview();
      await loadTabData();
    } catch (err) {
      alert(err.message || 'Verification approval failed.');
    } finally {
      setIsProcessingAction(false);
    }
  };

  const handleConfirmReject = async (e) => {
    e.preventDefault();
    if (!rejectingPharmacy || !rejectionReason.trim()) {
      alert('Please provide a specific rejection reason.');
      return;
    }
    setIsProcessingAction(true);
    try {
      await portalService.verifyAdminPharmacy(rejectingPharmacy.id, 'reject', rejectionReason.trim());
      setRejectingPharmacy(null);
      setRejectionReason('');
      await loadOverview();
      await loadTabData();
    } catch (err) {
      alert(err.message || 'Rejection failed.');
    } finally {
      setIsProcessingAction(false);
    }
  };

  // Medicine Creation Action
  const handleCreateMedicine = async (e) => {
    e.preventDefault();
    if (!newMedData.generic_name.trim() || !newMedData.strength.trim()) {
      alert('Generic name and strength are required.');
      return;
    }

    try {
      const aliases = newMedData.search_aliases
        ? newMedData.search_aliases.split(',').map((s) => s.trim()).filter(Boolean)
        : [];

      await portalService.createAdminMedicine({
        ...newMedData,
        search_aliases: aliases,
      });

      setShowAddMedModal(false);
      setNewMedData({
        generic_name: '',
        brand_name: '',
        strength: '',
        dosage_form: 'Tablet',
        pack_size: 'Strip of 10',
        search_aliases: '',
      });
      await loadOverview();
      await loadTabData();
    } catch (err) {
      alert(err.message || 'Failed to create catalogue medicine.');
    }
  };

  return (
    <div className="responsive-page-container" style={{ maxWidth: '1200px', margin: '30px auto 80px', padding: '0 20px' }}>
      {/* Admin Header */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        padding: 'clamp(18px, 3vw, 24px) clamp(18px, 3.5vw, 32px)',
        border: '1px solid #E2E8F0',
        boxShadow: '0 2px 12px rgba(18, 48, 71, 0.05)',
        marginBottom: '24px',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '50px',
            height: '50px',
            borderRadius: '12px',
            backgroundColor: '#F5F3FF',
            color: '#6D28D9',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                Platform Administration
              </h1>
              <span style={{
                backgroundColor: '#F5F3FF',
                color: '#6D28D9',
                border: '1px solid #DDD6FE',
                padding: '2px 8px',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 700
              }}>
                ADMIN CONSOLE
              </span>
            </div>
            <p style={{ margin: '4px 0 0 0', color: '#64748B', fontSize: '0.88rem' }}>
              Logged in as <strong>{user?.username}</strong> • Regulatory oversight & network operations
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => { loadOverview(); loadTabData(); }}
            style={{
              padding: '8px 14px',
              backgroundColor: '#F8FAFC',
              color: 'var(--color-navy-700, #123047)',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            Refresh Data
          </button>
          <button
            onClick={logout}
            style={{
              padding: '8px 14px',
              backgroundColor: '#F8FAFC',
              color: '#475569',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 500,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            Log Out
          </button>
        </div>
      </div>

      {/* Platform Metric Overview Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '14px',
        marginBottom: '24px'
      }}>
        <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748B', textTransform: 'uppercase' }}>Total Users</span>
          <p style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: '4px 0 0 0' }}>
            {overview?.total_users ?? '—'}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748B', textTransform: 'uppercase' }}>Pharmacists</span>
          <p style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: '4px 0 0 0' }}>
            {overview?.total_pharmacists ?? '—'}
          </p>
        </div>

        <div style={{
          backgroundColor: (overview?.pending_pharmacies || 0) > 0 ? '#FFFBEB' : '#FFFFFF',
          padding: '16px',
          borderRadius: '12px',
          border: `1px solid ${(overview?.pending_pharmacies || 0) > 0 ? '#FDE68A' : '#E2E8F0'}`,
          boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)'
        }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: (overview?.pending_pharmacies || 0) > 0 ? '#B45309' : '#64748B', textTransform: 'uppercase' }}>
            Pending Verification
          </span>
          <p style={{ fontSize: '1.6rem', fontWeight: 700, color: (overview?.pending_pharmacies || 0) > 0 ? '#B45309' : 'var(--color-navy-800, #123047)', margin: '4px 0 0 0' }}>
            {overview?.pending_pharmacies ?? '—'}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#059669', textTransform: 'uppercase' }}>Verified Pharmacies</span>
          <p style={{ fontSize: '1.6rem', fontWeight: 700, color: '#047857', margin: '4px 0 0 0' }}>
            {overview?.verified_pharmacies ?? '—'}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748B', textTransform: 'uppercase' }}>Catalogue Medicines</span>
          <p style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: '4px 0 0 0' }}>
            {overview?.total_medicines ?? '—'}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748B', textTransform: 'uppercase' }}>Stock Records</span>
          <p style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: '4px 0 0 0' }}>
            {overview?.total_inventories ?? '—'}
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="responsive-tab-bar" style={{
        display: 'flex',
        gap: '4px',
        borderBottom: '2px solid #E2E8F0',
        marginBottom: '20px',
        overflowX: 'auto',
        WebkitOverflowScrolling: 'touch',
        whiteSpace: 'nowrap'
      }}>
        <button
          onClick={() => setActiveTab('verifications')}
          style={{
            padding: '10px 18px',
            minHeight: '44px',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'verifications' ? '2px solid var(--color-teal-600, #0F766E)' : '2px solid transparent',
            color: activeTab === 'verifications' ? 'var(--color-teal-700, #0F766E)' : '#64748B',
            fontWeight: activeTab === 'verifications' ? 700 : 500,
            fontSize: '0.92rem',
            cursor: 'pointer',
            marginBottom: '-2px'
          }}
        >
          Pharmacy Verifications {(overview?.pending_pharmacies || 0) > 0 && `(${overview.pending_pharmacies})`}
        </button>
        <button
          onClick={() => setActiveTab('catalogue')}
          style={{
            padding: '10px 18px',
            minHeight: '44px',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'catalogue' ? '2px solid var(--color-teal-600, #0F766E)' : '2px solid transparent',
            color: activeTab === 'catalogue' ? 'var(--color-teal-700, #0F766E)' : '#64748B',
            fontWeight: activeTab === 'catalogue' ? 700 : 500,
            fontSize: '0.92rem',
            cursor: 'pointer',
            marginBottom: '-2px'
          }}
        >
          Medicine Catalogue ({overview?.total_medicines || 0})
        </button>
        <button
          onClick={() => setActiveTab('users')}
          style={{
            padding: '10px 18px',
            minHeight: '44px',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'users' ? '2px solid var(--color-teal-600, #0F766E)' : '2px solid transparent',
            color: activeTab === 'users' ? 'var(--color-teal-700, #0F766E)' : '#64748B',
            fontWeight: activeTab === 'users' ? 700 : 500,
            fontSize: '0.92rem',
            cursor: 'pointer',
            marginBottom: '-2px'
          }}
        >
          Registered Accounts
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          style={{
            padding: '10px 18px',
            minHeight: '44px',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'audit' ? '2px solid var(--color-teal-600, #0F766E)' : '2px solid transparent',
            color: activeTab === 'audit' ? 'var(--color-teal-700, #0F766E)' : '#64748B',
            fontWeight: activeTab === 'audit' ? 700 : 500,
            fontSize: '0.92rem',
            cursor: 'pointer',
            marginBottom: '-2px'
          }}
        >
          Audit History
        </button>
      </div>

      {/* TAB 1: PHARMACY VERIFICATIONS */}
      {activeTab === 'verifications' && (
        <div style={{ backgroundColor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['PENDING', 'VERIFIED', 'REJECTED', ''].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    backgroundColor: statusFilter === st ? 'var(--color-navy-800, #123047)' : '#FFFFFF',
                    color: statusFilter === st ? '#FFFFFF' : '#334155',
                    cursor: 'pointer'
                  }}
                >
                  {st === '' ? 'ALL PHARMACIES' : st}
                </button>
              ))}
            </div>
            <span style={{ fontSize: '0.85rem', color: '#64748B' }}>
              Showing {pharmacies.length} pharmacy records
            </span>
          </div>

          {pharmacies.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#64748B' }}>
              No pharmacies matching the selected status filter.
            </div>
          ) : (
            <div className="responsive-table-scroll" style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
              <table style={{ width: '100%', minWidth: '700px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
                <thead>
                  <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: 'var(--color-navy-700, #123047)' }}>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Pharmacy Name</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>License Credential</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Location</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Owner Account</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Status</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pharmacies.map((p) => {
                    const isPending = p.verification_status === 'PENDING';
                    const isVerified = p.verification_status === 'VERIFIED';

                    return (
                      <tr key={p.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                        <td style={{ padding: '12px 16px' }}>
                          <div style={{ fontWeight: 600, color: 'var(--color-navy-900, #0B1926)' }}>{p.name}</div>
                          <div style={{ fontSize: '0.78rem', color: '#64748B' }}>{p.contact_number || 'No contact provided'}</div>
                        </td>
                        <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontWeight: 600 }}>
                          {p.license_number || 'PENDING SUBMISSION'}
                        </td>
                        <td style={{ padding: '12px 16px', color: '#334155' }}>
                          {p.area}, {p.city} ({p.pin_code})
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          <div style={{ fontWeight: 500 }}>{p.owner_username || 'Unassigned'}</div>
                          <div style={{ fontSize: '0.78rem', color: '#64748B' }}>{p.owner_email || '—'}</div>
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          <span style={{
                            padding: '3px 8px',
                            borderRadius: '999px',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            backgroundColor: isVerified ? '#ECFDF5' : isPending ? '#FFFBEB' : '#FEF2F2',
                            color: isVerified ? '#047857' : isPending ? '#B45309' : '#BE123C',
                            border: `1px solid ${isVerified ? '#A7F3D0' : isPending ? '#FDE68A' : '#FECDD3'}`
                          }}>
                            {p.verification_status}
                          </span>
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                          {isPending ? (
                            <div style={{ display: 'inline-flex', gap: '6px' }}>
                              <button
                                onClick={() => handleApprovePharmacy(p.id, p.name)}
                                disabled={isProcessingAction}
                                style={{
                                  padding: '5px 10px',
                                  backgroundColor: 'var(--color-teal-600, #0F766E)',
                                  color: '#FFFFFF',
                                  border: 'none',
                                  borderRadius: '6px',
                                  fontSize: '0.78rem',
                                  fontWeight: 600,
                                  cursor: 'pointer'
                                }}
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => {
                                  setRejectingPharmacy(p);
                                  setRejectionReason('');
                                }}
                                disabled={isProcessingAction}
                                style={{
                                  padding: '5px 10px',
                                  backgroundColor: '#FEF2F2',
                                  color: '#B91C1C',
                                  border: '1px solid #FECDD3',
                                  borderRadius: '6px',
                                  fontSize: '0.78rem',
                                  fontWeight: 600,
                                  cursor: 'pointer'
                                }}
                              >
                                Reject
                              </button>
                            </div>
                          ) : (
                            <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>
                              {isVerified ? `Verified by ${p.verified_by_username || 'Admin'}` : 'Application Rejected'}
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: MEDICINE CATALOGUE */}
      {activeTab === 'catalogue' && (
        <div style={{ backgroundColor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
            <input
              type="text"
              placeholder="Search catalogue by name or brand..."
              value={medSearch}
              onChange={(e) => setMedSearch(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '0.88rem',
                minWidth: '280px'
              }}
            />

            <button
              onClick={() => setShowAddMedModal(true)}
              style={{
                padding: '8px 16px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                borderRadius: '8px',
                border: 'none',
                fontWeight: 600,
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              + Create New Medicine
            </button>
          </div>

          <div className="responsive-table-scroll" style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
            <table style={{ width: '100%', minWidth: '700px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: 'var(--color-navy-700, #123047)' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Active Generic Ingredient</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Brand Name</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Strength</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Dosage Form</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Pack Size</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Search Aliases</th>
                </tr>
              </thead>
              <tbody>
                {medicines.map((m) => (
                  <tr key={m.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy-900, #0B1926)' }}>
                      {m.generic_name}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#334155' }}>
                      {m.brand_name || 'Generic Formulation'}
                    </td>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-teal-700, #0F766E)' }}>
                      {m.strength}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#64748B' }}>
                      {m.dosage_form}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#64748B' }}>
                      {m.pack_size || 'Standard'}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '0.8rem', color: '#64748B' }}>
                      {Array.isArray(m.search_aliases) ? m.search_aliases.join(', ') : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: REGISTERED USERS */}
      {activeTab === 'users' && (
        <div style={{ backgroundColor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0', overflow: 'hidden' }}>
          <div className="responsive-table-scroll" style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
            <table style={{ width: '100%', minWidth: '700px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: 'var(--color-navy-700, #123047)' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Username</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Email Address</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Role</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Associated Pharmacy</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Registered Date</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Account Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy-900, #0B1926)' }}>
                      {u.username}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#64748B' }}>
                      {u.email || 'None provided'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        backgroundColor: u.role === 'ADMIN' ? '#F5F3FF' : u.role === 'PHARMACIST' ? '#ECFDF5' : '#F1F5F9',
                        color: u.role === 'ADMIN' ? '#6D28D9' : u.role === 'PHARMACIST' ? '#047857' : '#334155'
                      }}>
                        {u.role}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: '#334155' }}>
                      {u.pharmacy_name || '—'}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#64748B', fontSize: '0.82rem' }}>
                      {u.date_joined ? new Date(u.date_joined).toLocaleDateString() : '—'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ fontSize: '0.8rem', color: u.is_active ? '#059669' : '#DC2626', fontWeight: 600 }}>
                        {u.is_active ? 'Active' : 'Disabled'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: AUDIT TRAIL */}
      {activeTab === 'audit' && (
        <div style={{ backgroundColor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0', overflow: 'hidden' }}>
          <div className="responsive-table-scroll" style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
            <table style={{ width: '100%', minWidth: '700px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: 'var(--color-navy-700, #123047)' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Timestamp</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Actor</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Action</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Target Entity</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>IP Address</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>Metadata</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '10px 16px', color: '#64748B', whiteSpace: 'nowrap' }}>
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : '—'}
                    </td>
                    <td style={{ padding: '10px 16px', fontWeight: 600, color: 'var(--color-navy-800, #123047)' }}>
                      {log.actor_username || 'System'}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{
                        padding: '2px 6px',
                        borderRadius: '4px',
                        backgroundColor: '#F1F5F9',
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: 'var(--color-navy-700, #123047)'
                      }}>
                        {log.action}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px', color: '#334155' }}>
                      {log.target_type} ({log.target_id})
                    </td>
                    <td style={{ padding: '10px 16px', color: '#94A3B8', fontFamily: 'monospace', fontSize: '0.78rem' }}>
                      {log.ip_address || '127.0.0.1'}
                    </td>
                    <td style={{ padding: '10px 16px', color: '#64748B', fontSize: '0.78rem', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {JSON.stringify(log.metadata || {})}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* REJECT PHARMACY MODAL */}
      {rejectingPharmacy && (
        <div className="responsive-modal-overlay" style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.45)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 9999, padding: '16px'
        }}>
          <div className="responsive-modal-window" style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '16px',
            maxWidth: '480px',
            width: '100%',
            padding: 'clamp(20px, 3.5vw, 28px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', fontWeight: 700, color: '#B91C1C' }}>
              Reject Pharmacy Application
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#64748B', margin: '0 0 16px 0' }}>
              Rejecting <strong>{rejectingPharmacy.name}</strong>. Please provide a clear explanation for the applicant.
            </p>

            <form onSubmit={handleConfirmReject}>
              <div style={{ marginBottom: '18px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
                  Rejection Reason *
                </label>
                <textarea
                  rows="4"
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="e.g. License number DL-KA-2024-00129 does not match registered trade name in Karnataka Drug Control registry."
                  required
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid #CBD5E1',
                    fontSize: '16px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setRejectingPharmacy(null)}
                  style={{
                    padding: '10px 16px',
                    minHeight: '44px',
                    backgroundColor: '#F1F5F9',
                    color: '#334155',
                    border: '1px solid #CBD5E1',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isProcessingAction}
                  style={{
                    padding: '10px 20px',
                    minHeight: '44px',
                    backgroundColor: '#DC2626',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: isProcessingAction ? 'not-allowed' : 'pointer'
                  }}
                >
                  {isProcessingAction ? 'Rejecting...' : 'Confirm Rejection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ADD CATALOGUE MEDICINE MODAL */}
      {showAddMedModal && (
        <div className="responsive-modal-overlay" style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.45)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 9999, padding: '16px'
        }}>
          <div className="responsive-modal-window" style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '16px',
            maxWidth: '520px',
            width: '100%',
            padding: 'clamp(20px, 3.5vw, 28px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                Add Medicine to Formulary
              </h3>
              <button
                onClick={() => setShowAddMedModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#64748B', cursor: 'pointer', padding: '4px 8px' }}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreateMedicine}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                  Generic / Chemical Compound Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Ibuprofen"
                  value={newMedData.generic_name}
                  onChange={(e) => setNewMedData({ ...newMedData, generic_name: e.target.value })}
                  required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Brand / Trade Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Brufen"
                    value={newMedData.brand_name}
                    onChange={(e) => setNewMedData({ ...newMedData, brand_name: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Strength Concentration *
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 400mg"
                    value={newMedData.strength}
                    onChange={(e) => setNewMedData({ ...newMedData, strength: e.target.value })}
                    required
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Dosage Form *
                  </label>
                  <select
                    value={newMedData.dosage_form}
                    onChange={(e) => setNewMedData({ ...newMedData, dosage_form: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  >
                    <option value="Tablet">Tablet</option>
                    <option value="Capsule">Capsule</option>
                    <option value="Syrup">Syrup</option>
                    <option value="Suspension">Suspension</option>
                    <option value="Injection">Injection</option>
                    <option value="Drops">Drops</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Pack Size Unit
                  </label>
                  <input
                    type="text"
                    placeholder="Strip of 10"
                    value={newMedData.pack_size}
                    onChange={(e) => setNewMedData({ ...newMedData, pack_size: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                  Search Aliases (Comma-separated synonyms)
                </label>
                <input
                  type="text"
                  placeholder="e.g. brufen 400, painkiller, ibuprofen 400"
                  value={newMedData.search_aliases}
                  onChange={(e) => setNewMedData({ ...newMedData, search_aliases: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setShowAddMedModal(false)}
                  style={{
                    padding: '10px 16px',
                    minHeight: '44px',
                    backgroundColor: '#F1F5F9',
                    color: '#334155',
                    border: '1px solid #CBD5E1',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '10px 22px',
                    minHeight: '44px',
                    backgroundColor: 'var(--color-teal-600, #0F766E)',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Create Medicine
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
