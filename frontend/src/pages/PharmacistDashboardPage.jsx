/**
 * Pharmacist Dashboard (/pharmacist/dashboard)
 * Comprehensive pharmacy management with:
 * 1. Add / Register Pharmacy establishment
 * 2. Excel / CSV Bulk Stock Import and Template Export
 * 3. Excel-like interactive stock management table
 * 4. Real-time availability status tracking
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from '../context/RouterContext';
import { portalService } from '../services/portalService';

export default function PharmacistDashboardPage() {
  const { user, logout } = useAuth();
  const { navigate } = useRouter();

  const [pharmacy, setPharmacy] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tableFilter, setTableFilter] = useState('');

  // Modals
  const [showPharmacyModal, setShowPharmacyModal] = useState(false);
  const [showAddSingleModal, setShowAddSingleModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Pharmacy Form State
  const [pharmacyFormData, setPharmacyFormData] = useState({
    name: '',
    license_number: '',
    address: '',
    area: '',
    city: 'Bengaluru',
    pin_code: '560038',
    contact_number: '',
  });

  // Single Add Form State
  const [catalogSearch, setCatalogSearch] = useState('');
  const [catalogMedicines, setCatalogMedicines] = useState([]);
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  const [customMedName, setCustomMedName] = useState('');
  const [customStrength, setCustomStrength] = useState('500mg');
  const [customDosage, setCustomDosage] = useState('Tablet');
  const [addQuantity, setAddQuantity] = useState('');
  const [addPrice, setAddPrice] = useState('');
  const [singleModalError, setSingleModalError] = useState(null);
  const [isSubmittingSingle, setIsSubmittingSingle] = useState(false);

  // Bulk Import State
  const [bulkCsvText, setBulkCsvText] = useState('');
  const [parsedBulkItems, setParsedBulkItems] = useState([]);
  const [bulkError, setBulkError] = useState(null);
  const [isSubmittingBulk, setIsSubmittingBulk] = useState(false);
  const fileInputRef = useRef(null);

  // Edit Item State
  const [editQuantity, setEditQuantity] = useState('');
  const [editPrice, setEditPrice] = useState('');

  // Load pharmacy data and inventory
  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    try {
      const pharmData = await portalService.getPharmacistPharmacy();
      if (pharmData && pharmData.id) {
        setPharmacy(pharmData);
        setPharmacyFormData({
          name: pharmData.name || '',
          license_number: pharmData.license_number || '',
          address: pharmData.address || '',
          area: pharmData.area || '',
          city: pharmData.city || 'Bengaluru',
          pin_code: pharmData.pin_code || '560038',
          contact_number: pharmData.contact_number || '',
        });
      } else {
        setPharmacy(null);
      }

      const invData = await portalService.getPharmacistInventory();
      setInventory(invData.inventory || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Catalog search for single item add
  useEffect(() => {
    if (!showAddSingleModal) return;
    const fetchCatalog = async () => {
      try {
        const meds = await portalService.getPharmacistMedicineCatalog(catalogSearch);
        setCatalogMedicines(meds || []);
      } catch {
        setCatalogMedicines([]);
      }
    };
    const timer = setTimeout(fetchCatalog, 200);
    return () => clearTimeout(timer);
  }, [catalogSearch, showAddSingleModal]);

  // Handle Add/Edit Pharmacy submission
  const handleSavePharmacy = async (e) => {
    e.preventDefault();
    if (!pharmacyFormData.name.trim()) {
      alert('Pharmacy name is required.');
      return;
    }
    try {
      await portalService.createPharmacistPharmacy(pharmacyFormData);
      setShowPharmacyModal(false);
      await loadDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to save pharmacy.');
    }
  };

  // Handle Single Stock Item Add
  const handleAddSingleSubmit = async (e) => {
    e.preventDefault();
    setSingleModalError(null);

    let medId = selectedMedicine?.id;

    if (!medId && !customMedName.trim()) {
      setSingleModalError('Please select a medicine from catalogue or enter a medicine name.');
      return;
    }

    if (addQuantity === '' || isNaN(Number(addQuantity)) || Number(addQuantity) < 0) {
      setSingleModalError('Please enter a valid non-negative stock quantity.');
      return;
    }

    setIsSubmittingSingle(true);
    try {
      if (medId) {
        await portalService.addPharmacistInventory({
          medicine_id: medId,
          quantity: parseInt(addQuantity, 10),
          price: addPrice ? parseFloat(addPrice) : null,
        });
      } else {
        // Use bulk import endpoint to create new custom medicine on-the-fly
        await portalService.bulkImportPharmacistInventory([
          {
            generic_name: customMedName.trim(),
            strength: customStrength.trim() || '500mg',
            dosage_form: customDosage || 'Tablet',
            pack_size: 'Standard Unit',
            quantity: parseInt(addQuantity, 10),
            price: addPrice ? parseFloat(addPrice) : null,
          },
        ]);
      }

      setShowAddSingleModal(false);
      setSelectedMedicine(null);
      setCustomMedName('');
      setAddQuantity('');
      setAddPrice('');
      await loadDashboardData();
    } catch (err) {
      setSingleModalError(err.message || 'Failed to add stock item.');
    } finally {
      setIsSubmittingSingle(false);
    }
  };

  // CSV Parsing helper
  const parseCsvLines = (text) => {
    const lines = text.trim().split(/\r?\n/).filter(Boolean);
    if (lines.length === 0) return [];

    const items = [];
    const startIndex = lines[0].toLowerCase().includes('name') || lines[0].toLowerCase().includes('generic') ? 1 : 0;

    for (let i = startIndex; i < lines.length; i++) {
      const cols = lines[i].split(',').map((c) => c.trim().replace(/^["']|["']$/g, ''));
      if (cols.length >= 2 && cols[0]) {
        items.push({
          generic_name: cols[0],
          brand_name: cols[1] || '',
          strength: cols[2] || '500mg',
          dosage_form: cols[3] || 'Tablet',
          pack_size: cols[4] || 'Strip of 10',
          quantity: parseInt(cols[5], 10) || 0,
          price: parseFloat(cols[6]) || 0.0,
        });
      }
    }
    return items;
  };

  // Handle CSV file selection
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result;
      if (typeof text === 'string') {
        setBulkCsvText(text);
        const parsed = parseCsvLines(text);
        setParsedBulkItems(parsed);
      }
    };
    reader.readAsText(file);
  };

  const handleBulkTextChange = (text) => {
    setBulkCsvText(text);
    const parsed = parseCsvLines(text);
    setParsedBulkItems(parsed);
  };

  // Submit Bulk Stock Import
  const handleBulkImportSubmit = async (e) => {
    e.preventDefault();
    setBulkError(null);

    const itemsToImport = parsedBulkItems.length > 0 ? parsedBulkItems : parseCsvLines(bulkCsvText);
    if (itemsToImport.length === 0) {
      setBulkError('No valid medicine rows detected. Please check your CSV format or paste data.');
      return;
    }

    setIsSubmittingBulk(true);
    try {
      await portalService.bulkImportPharmacistInventory(itemsToImport);
      setShowBulkModal(false);
      setBulkCsvText('');
      setParsedBulkItems([]);
      await loadDashboardData();
    } catch (err) {
      setBulkError(err.message || 'Bulk import failed. Please verify the rows.');
    } finally {
      setIsSubmittingBulk(false);
    }
  };

  // Download Sample CSV template
  const handleDownloadSampleCsv = () => {
    const sampleContent =
      'Generic Name,Brand Name,Strength,Dosage Form,Pack Size,Quantity,Price\n' +
      'Paracetamol,Crocin,500mg,Tablet,Strip of 10,120,25.00\n' +
      'Paracetamol,Dolo,650mg,Tablet,Strip of 15,80,32.50\n' +
      'Amoxicillin,Novamox,500mg,Capsule,Strip of 10,45,68.00\n' +
      'Cetirizine,Cetzine,10mg,Tablet,Strip of 10,150,18.00\n' +
      'Azithromycin,Azithral,500mg,Tablet,Strip of 5,30,115.00\n' +
      'Pantoprazole,Pan 40,40mg,Tablet,Strip of 15,90,75.00\n';

    const blob = new Blob([sampleContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'medilocate_stock_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Export current inventory to CSV
  const handleExportStockToCsv = () => {
    if (inventory.length === 0) {
      alert('No inventory to export.');
      return;
    }

    let csvContent = 'Medicine Name,Brand Name,Strength,Dosage Form,Pack Size,Quantity,Price,Availability Status\n';
    inventory.forEach((item) => {
      const med = item.medicine_details || {};
      csvContent += `"${med.generic_name || ''}","${med.brand_name || ''}","${med.strength || ''}","${med.dosage_form || ''}","${med.pack_size || ''}",${item.quantity ?? 0},${item.price ?? 0},"${item.availability_label || item.availability_status}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${(pharmacy?.name || 'pharmacy').replace(/\s+/g, '_')}_inventory.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Update single item inline
  const handleUpdateStock = async (e) => {
    e.preventDefault();
    if (!editingItem) return;

    try {
      await portalService.updatePharmacistInventory(editingItem.id, {
        quantity: editQuantity !== '' ? parseInt(editQuantity, 10) : null,
        price: editPrice !== '' ? parseFloat(editPrice) : null,
      });
      setEditingItem(null);
      await loadDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to update item.');
    }
  };

  // Delete inventory item
  const handleDeleteStock = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove ${name} from your inventory?`)) {
      return;
    }
    try {
      await portalService.deletePharmacistInventory(id);
      await loadDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to delete item.');
    }
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--color-navy-700, #123047)' }}>
        <p style={{ fontWeight: 600 }}>Loading Pharmacist Workspace...</p>
      </div>
    );
  }

  // Filtered Inventory list
  const filteredInventory = inventory.filter((item) => {
    if (!tableFilter.trim()) return true;
    const term = tableFilter.toLowerCase();
    const med = item.medicine_details || {};
    return (
      (med.generic_name && med.generic_name.toLowerCase().includes(term)) ||
      (med.brand_name && med.brand_name.toLowerCase().includes(term)) ||
      (item.availability_status && item.availability_status.toLowerCase().includes(term)) ||
      (item.availability_label && item.availability_label.toLowerCase().includes(term))
    );
  });

  const totalStockCount = inventory.length;
  const availableCount = inventory.filter((i) => i.availability_status === 'AVAILABLE').length;
  const lowStockCount = inventory.filter((i) => i.availability_status === 'LOW_STOCK').length;
  const outOfStockCount = inventory.filter((i) => i.availability_status === 'OUT_OF_STOCK').length;

  const isVerified = pharmacy?.verification_status === 'VERIFIED';
  const isPending = pharmacy?.verification_status === 'PENDING';
  const isRejected = pharmacy?.verification_status === 'REJECTED';

  return (
    <div className="responsive-page-container" style={{ maxWidth: '1200px', margin: '30px auto 80px', padding: '0 20px' }}>
      {/* Top Header Card */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        padding: 'clamp(18px, 3vw, 24px) clamp(18px, 3.5vw, 30px)',
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
            width: '52px',
            height: '52px',
            borderRadius: '12px',
            backgroundColor: isVerified
              ? 'var(--color-mint-100, #D1FAE5)'
              : isPending
              ? '#FEF3C7'
              : isRejected
              ? '#FEE2E2'
              : '#F1F5F9',
            color: isVerified
              ? 'var(--color-teal-800, #0F766E)'
              : isPending
              ? '#B45309'
              : isRejected
              ? '#B91C1C'
              : '#475569',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <line x1="9" y1="12" x2="15" y2="12" />
              <line x1="12" y1="9" x2="12" y2="15" />
            </svg>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <h1 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                {pharmacy ? pharmacy.name : 'Register Your Pharmacy'}
              </h1>
              {pharmacy && isVerified && (
                <span style={{
                  backgroundColor: '#ECFDF5',
                  color: '#047857',
                  border: '1px solid #A7F3D0',
                  padding: '3px 10px',
                  borderRadius: '999px',
                  fontSize: '0.78rem',
                  fontWeight: 700
                }}>
                  ACTIVE ESTABLISHMENT • VERIFIED
                </span>
              )}
              {pharmacy && isPending && (
                <span style={{
                  backgroundColor: '#FFFBEB',
                  color: '#B45309',
                  border: '1px solid #FDE68A',
                  padding: '3px 10px',
                  borderRadius: '999px',
                  fontSize: '0.78rem',
                  fontWeight: 700
                }}>
                  PENDING VERIFICATION
                </span>
              )}
              {pharmacy && isRejected && (
                <span style={{
                  backgroundColor: '#FEF2F2',
                  color: '#B91C1C',
                  border: '1px solid #FCA5A5',
                  padding: '3px 10px',
                  borderRadius: '999px',
                  fontSize: '0.78rem',
                  fontWeight: 700
                }}>
                  APPLICATION REJECTED
                </span>
              )}
            </div>
            <p style={{ margin: '4px 0 0 0', color: '#64748B', fontSize: '0.88rem' }}>
              {pharmacy ? (
                <>
                  License: <strong>{pharmacy.license_number || 'Registered'}</strong> • {pharmacy.area}, {pharmacy.city} ({pharmacy.pin_code})
                </>
              ) : (
                'Add your pharmacy details to start stocking and managing medicines'
              )}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setShowPharmacyModal(true)}
            style={{
              padding: '9px 16px',
              backgroundColor: 'var(--color-teal-600, #0F766E)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            {pharmacy ? 'Edit Pharmacy Info' : 'Add Pharmacy'}
          </button>
          <button
            onClick={loadDashboardData}
            style={{
              padding: '9px 14px',
              backgroundColor: '#F8FAFC',
              color: 'var(--color-navy-700, #123047)',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer'
            }}
          >
            Refresh
          </button>
          <button
            onClick={logout}
            style={{
              padding: '9px 14px',
              backgroundColor: '#F8FAFC',
              color: '#475569',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 500,
              fontSize: '0.88rem',
              cursor: 'pointer'
            }}
          >
            Log Out
          </button>
        </div>
      </div>

      {/* Pending Verification Notice */}
      {pharmacy && isPending && (
        <div role="status" style={{
          backgroundColor: '#FFFBEB',
          border: '1px solid #FDE68A',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
          color: '#92400E'
        }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" style={{ flexShrink: 0, marginTop: '2px', color: '#D97706' }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>
            <strong style={{ display: 'block', fontSize: '0.98rem', marginBottom: '4px', color: '#B45309' }}>
              Pharmacy Establishment Pending Administrator Approval
            </strong>
            <span style={{ fontSize: '0.88rem', lineHeight: 1.5, color: '#78350F' }}>
              Your pharmacy application for <strong>{pharmacy.name}</strong> is currently pending regulatory review.
              Stock listing and inventory modifications remain locked until an administrator verifies your drug license credentials ({pharmacy.license_number || 'Pending'}).
            </span>
          </div>
        </div>
      )}

      {/* Rejected Application Notice */}
      {pharmacy && isRejected && (
        <div role="alert" style={{
          backgroundColor: '#FEF2F2',
          border: '1px solid #FCA5A5',
          borderRadius: '12px',
          padding: '18px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
          color: '#991B1B'
        }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" style={{ flexShrink: 0, marginTop: '2px', color: '#DC2626' }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          <div>
            <strong style={{ display: 'block', fontSize: '0.98rem', marginBottom: '4px', color: '#B91C1C' }}>
              Pharmacy Verification Application Rejected
            </strong>
            <p style={{ margin: '0 0 8px 0', fontSize: '0.88rem', lineHeight: 1.5, color: '#7F1D1D' }}>
              Your application was reviewed and rejected by the platform administrator. Stock publication and modifications are blocked.
            </p>
            {pharmacy.rejection_reason && (
              <div style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #FECACA',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.86rem',
                color: '#991B1B',
                marginBottom: '8px'
              }}>
                <strong>Administrator Feedback / Reason:</strong> {pharmacy.rejection_reason}
              </div>
            )}
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#7F1D1D' }}>
              Please click "Edit Pharmacy Info" above to correct your license number or establishment details and resubmit for review.
            </p>
          </div>
        </div>
      )}

      {/* If No Pharmacy Created Yet: Welcoming Banner with Add Button */}
      {!pharmacy && (
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          padding: '36px 32px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 4px 16px rgba(18, 48, 71, 0.06)',
          textAlign: 'center',
          marginBottom: '28px'
        }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            backgroundColor: 'var(--color-mint-50, #ECFDF5)',
            color: 'var(--color-teal-700, #0F766E)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <line x1="9" y1="12" x2="15" y2="12" />
              <line x1="12" y1="9" x2="12" y2="15" />
            </svg>
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', marginBottom: '8px' }}>
            Add Your Pharmacy Establishment
          </h2>
          <p style={{ color: '#64748B', maxWidth: '520px', margin: '0 auto 24px', fontSize: '0.95rem', lineHeight: 1.5 }}>
            To start listing medicines, importing stock from Excel, and receiving patient discovery traffic, please enter your pharmacy details.
          </p>
          <button
            onClick={() => setShowPharmacyModal(true)}
            style={{
              padding: '12px 28px',
              backgroundColor: 'var(--color-teal-600, #0F766E)',
              color: '#FFFFFF',
              borderRadius: '10px',
              fontWeight: 600,
              fontSize: '0.95rem',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(15, 118, 110, 0.25)'
            }}
          >
            + Add Pharmacy Now
          </button>
        </div>
      )}

      {/* Stock Metrics Overview Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{ backgroundColor: '#FFFFFF', padding: '18px 20px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#64748B', textTransform: 'uppercase' }}>Total Medicines</span>
          <p style={{ fontSize: '1.7rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: '4px 0 0 0' }}>
            {totalStockCount}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '18px 20px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#059669', textTransform: 'uppercase' }}>In Stock (Available)</span>
          <p style={{ fontSize: '1.7rem', fontWeight: 700, color: '#047857', margin: '4px 0 0 0' }}>
            {availableCount}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '18px 20px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#D97706', textTransform: 'uppercase' }}>Low Stock Alert (&lt;10)</span>
          <p style={{ fontSize: '1.7rem', fontWeight: 700, color: '#B45309', margin: '4px 0 0 0' }}>
            {lowStockCount}
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '18px 20px', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#DC2626', textTransform: 'uppercase' }}>Out of Stock (0)</span>
          <p style={{ fontSize: '1.7rem', fontWeight: 700, color: '#B91C1C', margin: '4px 0 0 0' }}>
            {outOfStockCount}
          </p>
        </div>
      </div>

      {/* Stock Management Box (Excel-like Interface) */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 16px rgba(18, 48, 71, 0.06)',
        overflow: 'hidden'
      }}>
        {/* Table Controls Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #E2E8F0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px'
        }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: 0 }}>
              Pharmacy Stock Sheet
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#64748B', margin: '3px 0 0 0' }}>
              Manage quantities and retail prices. Upload stock from Excel/CSV or edit directly in the sheet below.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              disabled={!isVerified}
              title={!isVerified ? 'Requires a verified pharmacy establishment' : 'Import stock from CSV'}
              onClick={() => {
                if (!isVerified) return;
                setShowBulkModal(true);
                setBulkError(null);
                setBulkCsvText('');
                setParsedBulkItems([]);
              }}
              style={{
                padding: '9px 16px',
                backgroundColor: isVerified ? '#ECFDF5' : '#F1F5F9',
                color: isVerified ? '#047857' : '#94A3B8',
                border: `1px solid ${isVerified ? '#A7F3D0' : '#E2E8F0'}`,
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.88rem',
                cursor: isVerified ? 'pointer' : 'not-allowed',
                opacity: isVerified ? 1 : 0.6,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              Import Excel / CSV
            </button>

            <button
              disabled={inventory.length === 0}
              onClick={handleExportStockToCsv}
              style={{
                padding: '9px 14px',
                backgroundColor: '#F8FAFC',
                color: inventory.length > 0 ? 'var(--color-navy-700, #123047)' : '#94A3B8',
                border: '1px solid #CBD5E1',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.88rem',
                cursor: inventory.length > 0 ? 'pointer' : 'not-allowed',
                opacity: inventory.length > 0 ? 1 : 0.6,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Export CSV
            </button>

            <button
              disabled={!isVerified}
              title={!isVerified ? 'Requires a verified pharmacy establishment' : 'Add medicine stock'}
              onClick={() => {
                if (!isVerified) return;
                setShowAddSingleModal(true);
                setSingleModalError(null);
                setSelectedMedicine(null);
                setCustomMedName('');
                setAddQuantity('');
                setAddPrice('');
              }}
              style={{
                padding: '9px 18px',
                backgroundColor: isVerified ? 'var(--color-teal-600, #0F766E)' : '#CBD5E1',
                color: '#FFFFFF',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.88rem',
                border: 'none',
                cursor: isVerified ? 'pointer' : 'not-allowed',
                opacity: isVerified ? 1 : 0.6,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              + Add Medicine Stock
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div style={{ padding: '12px 24px', backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ position: 'relative', maxWidth: '340px', width: '100%' }}>
            <input
              type="text"
              placeholder="Filter stock by medicine name or status..."
              value={tableFilter}
              onChange={(e) => setTableFilter(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px 8px 34px',
                borderRadius: '6px',
                border: '1px solid #CBD5E1',
                fontSize: '0.85rem',
                boxSizing: 'border-box'
              }}
            />
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#64748B"
              strokeWidth="2"
              style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }}
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </div>
          <span style={{ fontSize: '0.82rem', color: '#64748B' }}>
            Showing <strong>{filteredInventory.length}</strong> of {inventory.length} records
          </span>
        </div>

        {/* Excel-like Inventory Table */}
        {filteredInventory.length === 0 ? (
          <div style={{ padding: '60px 20px', textAlign: 'center', color: '#64748B' }}>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 6px 0' }}>
              No inventory records found.
            </p>
            <p style={{ fontSize: '0.88rem', margin: '0 0 18px 0' }}>
              Add medicines individually or import your stock directly from an Excel / CSV spreadsheet.
            </p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button
                onClick={() => setShowBulkModal(true)}
                style={{
                  padding: '9px 18px',
                  backgroundColor: '#ECFDF5',
                  color: '#047857',
                  border: '1px solid #A7F3D0',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '0.88rem',
                  cursor: 'pointer'
                }}
              >
                Upload Excel / CSV File
              </button>
              <button
                onClick={() => setShowAddSingleModal(true)}
                style={{
                  padding: '9px 18px',
                  backgroundColor: 'var(--color-teal-600, #0F766E)',
                  color: '#FFFFFF',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '0.88rem',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                + Add Single Medicine
              </button>
            </div>
          </div>
        ) : (
          <div className="responsive-table-scroll" style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
            <table style={{ width: '100%', minWidth: '760px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#F1F5F9', borderBottom: '2px solid #CBD5E1', color: 'var(--color-navy-800, #123047)' }}>
                  <th style={{ padding: '10px 14px', width: '40px', fontWeight: 600 }}>#</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Medicine Name</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Brand</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Strength</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Form</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Pack Size</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Stock Qty</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Unit Price (INR)</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600 }}>Status</th>
                  <th style={{ padding: '10px 16px', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredInventory.map((item, index) => {
                  const med = item.medicine_details || {};
                  const isAvailable = item.availability_status === 'AVAILABLE';
                  const isLowStock = item.availability_status === 'LOW_STOCK';
                  const isOutOfStock = item.availability_status === 'OUT_OF_STOCK';

                  return (
                    <tr
                      key={item.id}
                      style={{
                        borderBottom: '1px solid #E2E8F0',
                        backgroundColor: index % 2 === 0 ? '#FFFFFF' : '#F8FAFC'
                      }}
                    >
                      <td style={{ padding: '12px 14px', color: '#94A3B8', fontWeight: 500 }}>
                        {index + 1}
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy-900, #0B1926)' }}>
                        {med.generic_name}
                      </td>
                      <td style={{ padding: '12px 16px', color: '#334155' }}>
                        {med.brand_name || 'Generic'}
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-teal-700, #0F766E)' }}>
                        {med.strength}
                      </td>
                      <td style={{ padding: '12px 16px', color: '#64748B' }}>
                        {med.dosage_form}
                      </td>
                      <td style={{ padding: '12px 16px', color: '#64748B' }}>
                        {med.pack_size || 'Strip of 10'}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{
                          fontWeight: 700,
                          fontSize: '0.95rem',
                          color: isOutOfStock ? '#DC2626' : isLowStock ? '#D97706' : '#0F766E'
                        }}>
                          {item.quantity !== null ? item.quantity : 0}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: 600, color: '#1E293B' }}>
                        {item.price ? `₹${Number(item.price).toFixed(2)}` : '₹0.00'}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{
                          padding: '3px 8px',
                          borderRadius: '999px',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          backgroundColor: isAvailable ? '#ECFDF5' : isLowStock ? '#FFFBEB' : '#FEF2F2',
                          color: isAvailable ? '#065F46' : isLowStock ? '#92400E' : '#991B1B',
                          border: `1px solid ${isAvailable ? '#A7F3D0' : isLowStock ? '#FDE68A' : '#FECDD3'}`
                        }}>
                          {item.availability_label || item.availability_status}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                        <button
                          onClick={() => {
                            setEditingItem(item);
                            setEditQuantity(item.quantity !== null ? item.quantity : '');
                            setEditPrice(item.price !== null ? item.price : '');
                          }}
                          style={{
                            padding: '4px 10px',
                            marginRight: '6px',
                            backgroundColor: '#FFFFFF',
                            color: 'var(--color-navy-700, #123047)',
                            border: '1px solid #CBD5E1',
                            borderRadius: '6px',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteStock(item.id, med.generic_name)}
                          style={{
                            padding: '4px 8px',
                            backgroundColor: '#FEF2F2',
                            color: '#B91C1C',
                            border: '1px solid #FECDD3',
                            borderRadius: '6px',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* =====================================================================
          MODAL 1: ADD / REGISTER PHARMACY
          ===================================================================== */}
      {showPharmacyModal && (
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
            maxWidth: '540px',
            width: '100%',
            padding: 'clamp(20px, 3.5vw, 28px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                {pharmacy ? 'Edit Pharmacy Details' : 'Register Pharmacy Establishment'}
              </h3>
              <button
                onClick={() => setShowPharmacyModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#64748B', cursor: 'pointer', padding: '4px 8px' }}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSavePharmacy}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                  Pharmacy Trading Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. MedPlus Pharmacy"
                  value={pharmacyFormData.name}
                  onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, name: e.target.value })}
                  required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Drug License Number *
                  </label>
                  <input
                    type="text"
                    placeholder="DL-KA-2024-88991"
                    value={pharmacyFormData.license_number}
                    onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, license_number: e.target.value })}
                    required
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    placeholder="+91 99887 76655"
                    value={pharmacyFormData.contact_number}
                    onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, contact_number: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                  Street Address
                </label>
                <input
                  type="text"
                  placeholder="Building No, 1st Main Road"
                  value={pharmacyFormData.address}
                  onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, address: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', marginBottom: '22px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Area / Locality
                  </label>
                  <input
                    type="text"
                    placeholder="Indiranagar"
                    value={pharmacyFormData.area}
                    onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, area: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    City
                  </label>
                  <input
                    type="text"
                    placeholder="Bengaluru"
                    value={pharmacyFormData.city}
                    onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, city: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    PIN Code
                  </label>
                  <input
                    type="text"
                    placeholder="560038"
                    value={pharmacyFormData.pin_code}
                    onChange={(e) => setPharmacyFormData({ ...pharmacyFormData, pin_code: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setShowPharmacyModal(false)}
                  style={{ padding: '10px 18px', minHeight: '44px', backgroundColor: '#F1F5F9', color: '#334155', border: '1px solid #CBD5E1', borderRadius: '8px', fontSize: '0.88rem', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: '10px 22px', minHeight: '44px', backgroundColor: 'var(--color-teal-600, #0F766E)', color: '#FFFFFF', border: 'none', borderRadius: '8px', fontSize: '0.88rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Save Pharmacy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 2: BULK EXCEL / CSV STOCK IMPORT
          ===================================================================== */}
      {showBulkModal && (
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
            maxWidth: '680px',
            width: '100%',
            padding: 'clamp(20px, 3.5vw, 28px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                  Import Stock from Excel / CSV
                </h3>
                <p style={{ margin: '3px 0 0 0', fontSize: '0.85rem', color: '#64748B' }}>
                  Upload a spreadsheet or paste comma-separated stock rows
                </p>
              </div>
              <button
                onClick={() => setShowBulkModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#64748B', cursor: 'pointer', padding: '4px 8px' }}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            {bulkError && (
              <div role="alert" style={{
                backgroundColor: '#FEF2F2',
                border: '1px solid #FCA5A5',
                color: '#B91C1C',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.88rem',
                marginBottom: '16px'
              }}>
                {bulkError}
              </div>
            )}

            {/* Template Download Row */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 16px',
              backgroundColor: '#F8FAFC',
              borderRadius: '8px',
              border: '1px solid #E2E8F0',
              marginBottom: '18px',
              flexWrap: 'wrap',
              gap: '10px'
            }}>
              <div>
                <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--color-navy-800, #123047)' }}>
                  Excel / CSV Template Format:
                </span>
                <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: '#64748B' }}>
                  Columns: Generic Name, Brand, Strength, Dosage, Pack Size, Quantity, Price
                </p>
              </div>
              <button
                type="button"
                onClick={handleDownloadSampleCsv}
                style={{
                  padding: '9px 14px',
                  minHeight: '44px',
                  backgroundColor: '#FFFFFF',
                  color: 'var(--color-teal-700, #0F766E)',
                  border: '1px solid #99F6E4',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Download Sample Template
              </button>
            </div>

            {/* File Selector */}
            <div style={{ marginBottom: '16px' }}>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv, .txt, text/csv, application/vnd.ms-excel"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                style={{
                  width: '100%',
                  padding: '16px',
                  minHeight: '60px',
                  border: '2px dashed #CBD5E1',
                  borderRadius: '10px',
                  backgroundColor: '#F8FAFC',
                  cursor: 'pointer',
                  textAlign: 'center',
                  color: 'var(--color-navy-800, #123047)'
                }}
              >
                <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '4px' }}>
                  Click to select CSV / Excel file
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748B' }}>
                  or paste the raw CSV rows in the text box below
                </div>
              </button>
            </div>

            {/* Paste Box */}
            <div style={{ marginBottom: '18px' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
                Paste CSV Rows or Edit:
              </label>
              <textarea
                rows="6"
                placeholder={'Paracetamol, Crocin, 500mg, Tablet, Strip of 10, 100, 25.00\nAmoxicillin, Novamox, 500mg, Capsule, Strip of 10, 50, 65.00'}
                value={bulkCsvText}
                onChange={(e) => handleBulkTextChange(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '8px',
                  border: '1px solid #CBD5E1',
                  fontFamily: 'monospace',
                  fontSize: '16px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Parsed Rows Preview */}
            {parsedBulkItems.length > 0 && (
              <div style={{ marginBottom: '18px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#047857', marginBottom: '6px' }}>
                  Detected {parsedBulkItems.length} valid medicine rows ready to import:
                </div>
                <div className="responsive-table-scroll" style={{ maxHeight: '140px', overflowY: 'auto', overflowX: 'auto', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
                  <table style={{ width: '100%', minWidth: '400px', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#F1F5F9' }}>
                        <th style={{ padding: '6px 8px' }}>Medicine</th>
                        <th style={{ padding: '6px 8px' }}>Strength</th>
                        <th style={{ padding: '6px 8px' }}>Form</th>
                        <th style={{ padding: '6px 8px' }}>Qty</th>
                        <th style={{ padding: '6px 8px' }}>Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      {parsedBulkItems.map((row, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                          <td style={{ padding: '6px 8px', fontWeight: 600 }}>{row.generic_name}</td>
                          <td style={{ padding: '6px 8px' }}>{row.strength}</td>
                          <td style={{ padding: '6px 8px' }}>{row.dosage_form}</td>
                          <td style={{ padding: '6px 8px' }}>{row.quantity}</td>
                          <td style={{ padding: '6px 8px' }}>₹{row.price}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={() => setShowBulkModal(false)}
                style={{ padding: '10px 18px', minHeight: '44px', backgroundColor: '#F1F5F9', color: '#334155', border: '1px solid #CBD5E1', borderRadius: '8px', fontSize: '0.88rem', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleBulkImportSubmit}
                disabled={isSubmittingBulk}
                style={{
                  padding: '10px 22px',
                  minHeight: '44px',
                  backgroundColor: 'var(--color-teal-600, #0F766E)',
                  color: '#FFFFFF',
                  borderRadius: '8px',
                  border: 'none',
                  fontWeight: 600,
                  fontSize: '0.88rem',
                  cursor: isSubmittingBulk ? 'not-allowed' : 'pointer'
                }}
              >
                {isSubmittingBulk ? 'Importing Rows...' : `Import ${parsedBulkItems.length || ''} Stock Records`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 3: ADD SINGLE MEDICINE STOCK
          ===================================================================== */}
      {showAddSingleModal && (
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                Add Medicine to Stock
              </h3>
              <button
                onClick={() => setShowAddSingleModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#64748B', cursor: 'pointer', padding: '4px 8px' }}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            {singleModalError && (
              <div role="alert" style={{
                backgroundColor: '#FEF2F2',
                border: '1px solid #FCA5A5',
                color: '#B91C1C',
                padding: '10px 12px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                marginBottom: '16px'
              }}>
                {singleModalError}
              </div>
            )}

            <form onSubmit={handleAddSingleSubmit}>
              {/* Option A: Search Formulary */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
                  Select from Catalogue or Enter Custom Formulation:
                </label>
                <input
                  type="text"
                  placeholder="Type to filter catalogue (e.g. Paracetamol, Novamox)..."
                  value={catalogSearch}
                  onChange={(e) => setCatalogSearch(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', marginBottom: '6px', boxSizing: 'border-box' }}
                />

                <div style={{ maxHeight: '130px', overflowY: 'auto', border: '1px solid #E2E8F0', borderRadius: '6px', backgroundColor: '#F8FAFC' }}>
                  {catalogMedicines.map((m) => {
                    const isSel = selectedMedicine?.id === m.id;
                    return (
                      <div
                        key={m.id}
                        onClick={() => {
                          setSelectedMedicine(m);
                          setCustomMedName('');
                        }}
                        style={{
                          padding: '7px 12px',
                          borderBottom: '1px solid #F1F5F9',
                          cursor: 'pointer',
                          backgroundColor: isSel ? 'var(--color-mint-50, #ECFDF5)' : '#FFFFFF',
                          color: isSel ? 'var(--color-teal-800, #0F766E)' : 'inherit',
                          fontWeight: isSel ? 600 : 400,
                          fontSize: '0.85rem'
                        }}
                      >
                        {m.display_name} ({m.pack_size || 'Standard'})
                      </div>
                    );
                  })}
                </div>
              </div>

              {selectedMedicine ? (
                <div style={{
                  padding: '10px 12px',
                  backgroundColor: 'var(--color-mint-50, #ECFDF5)',
                  border: '1px solid #A7F3D0',
                  borderRadius: '6px',
                  marginBottom: '16px',
                  fontSize: '0.85rem',
                  color: 'var(--color-teal-800, #0F766E)'
                }}>
                  Selected Catalogue Item: <strong>{selectedMedicine.display_name}</strong>
                  <button
                    type="button"
                    onClick={() => setSelectedMedicine(null)}
                    style={{ marginLeft: '10px', background: 'none', border: 'none', color: '#B91C1C', cursor: 'pointer', textDecoration: 'underline', fontSize: '0.8rem' }}
                  >
                    Clear selection
                  </button>
                </div>
              ) : (
                <div style={{
                  padding: '12px',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '8px',
                  border: '1px solid #E2E8F0',
                  marginBottom: '16px'
                }}>
                  <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-navy-800, #123047)' }}>
                    Or Add Custom / New Medicine:
                  </span>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px', marginTop: '6px' }}>
                    <input
                      type="text"
                      placeholder="Medicine Name (e.g. Cefixime)"
                      value={customMedName}
                      onChange={(e) => setCustomMedName(e.target.value)}
                      style={{ padding: '8px 10px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px' }}
                    />
                    <input
                      type="text"
                      placeholder="Strength (e.g. 200mg)"
                      value={customStrength}
                      onChange={(e) => setCustomStrength(e.target.value)}
                      style={{ padding: '8px 10px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px' }}
                    />
                  </div>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '22px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Stock Quantity *
                  </label>
                  <input
                    type="number"
                    min="0"
                    placeholder="e.g. 50"
                    value={addQuantity}
                    onChange={(e) => setAddQuantity(e.target.value)}
                    required
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                    Unit Selling Price (INR)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="e.g. 45.00"
                    value={addPrice}
                    onChange={(e) => setAddPrice(e.target.value)}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setShowAddSingleModal(false)}
                  style={{ padding: '10px 18px', minHeight: '44px', backgroundColor: '#F1F5F9', color: '#334155', border: '1px solid #CBD5E1', borderRadius: '8px', fontSize: '0.88rem', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingSingle}
                  style={{
                    padding: '10px 22px',
                    minHeight: '44px',
                    backgroundColor: 'var(--color-teal-600, #0F766E)',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '0.88rem',
                    fontWeight: 600,
                    cursor: isSubmittingSingle ? 'not-allowed' : 'pointer'
                  }}
                >
                  {isSubmittingSingle ? 'Saving...' : 'Add to Sheet'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 4: EDIT STOCK ROW
          ===================================================================== */}
      {editingItem && (
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
            maxWidth: '440px',
            width: '100%',
            padding: 'clamp(20px, 3.5vw, 28px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                Edit Stock: {editingItem.medicine_details?.generic_name}
              </h3>
              <button
                onClick={() => setEditingItem(null)}
                style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#64748B', cursor: 'pointer', padding: '4px 8px' }}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleUpdateStock}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                  Available Stock Quantity
                </label>
                <input
                  type="number"
                  min="0"
                  value={editQuantity}
                  onChange={(e) => setEditQuantity(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                  Unit Selling Price (INR)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={editPrice}
                  onChange={(e) => setEditPrice(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setEditingItem(null)}
                  style={{ padding: '10px 16px', minHeight: '44px', backgroundColor: '#F1F5F9', color: '#334155', border: '1px solid #CBD5E1', borderRadius: '6px', fontSize: '0.85rem', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: '10px 20px', minHeight: '44px', backgroundColor: 'var(--color-teal-600, #0F766E)', color: '#FFFFFF', border: 'none', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
