import React, { useState } from 'react';
import './ProjectForm.css';

export default function ProjectForm() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectNumber, setProjectNumber] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('planned');
  const [clientName, setClientName] = useState('');
  const [projectManager, setProjectManager] = useState('');
  const [address, setAddress] = useState('');
  const [budget, setBudget] = useState('');
  const [originalBudget, setOriginalBudget] = useState('');
  const [revisedBudget, setRevisedBudget] = useState('');
  const [contingencyFund, setContingencyFund] = useState('');
  const [riskLevel, setRiskLevel] = useState('low');
  const [riskNotes, setRiskNotes] = useState('');
  const [mapUrl, setMapUrl] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [pictureUrl, setPictureUrl] = useState('');
  const [videoCaptureUrl, setVideoCaptureUrl] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [notes, setNotes] = useState('');
  const [planRepositoryUrl, setPlanRepositoryUrl] = useState('');
  const [sustainabilityRating, setSustainabilityRating] = useState('');
  const [sustainabilityGoals, setSustainabilityGoals] = useState('');
  const [collaborationUrl, setCollaborationUrl] = useState('');
  const [integrationStatus, setIntegrationStatus] = useState(false);
  const [auditDueDate, setAuditDueDate] = useState('');
  const [complianceStatus, setComplianceStatus] = useState('pending');
  const [localHires, setLocalHires] = useState('');
  const [communityEngagementNotes, setCommunityEngagementNotes] = useState('');
  const [previousProjectId, setPreviousProjectId] = useState('');
  const [benchmarkCostPerUnit, setBenchmarkCostPerUnit] = useState('');
  const [tags, setTags] = useState('');
  const [criticalPathDuration, setCriticalPathDuration] = useState('');
  const [keyMilestones, setKeyMilestones] = useState('');
  const [safetyIncidents, setSafetyIncidents] = useState('');
  const [incidentNotes, setIncidentNotes] = useState('');
  const [bimFileUrl, setBimFileUrl] = useState('');
  const [bimModelId, setBimModelId] = useState('');
  const [updatedBy, setUpdatedBy] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      name,
      description,
      project_number: projectNumber,
      category,
      status,
      client_name: clientName,
      project_manager: projectManager,
      address,
      budget,
      original_budget: originalBudget,
      revised_budget: revisedBudget,
      contingency_fund: contingencyFund,
      risk_level: riskLevel,
      risk_notes: riskNotes,
      map_url: mapUrl,
      latitude,
      longitude,
      picture_url: pictureUrl,
      video_capture_url: videoCaptureUrl,
      start_date: startDate,
      end_date: endDate,
      notes,
      plan_repository_url: planRepositoryUrl,
      sustainability_rating: sustainabilityRating,
      sustainability_goals: sustainabilityGoals,
      collaboration_url: collaborationUrl,
      integration_status: integrationStatus,
      audit_due_date: auditDueDate,
      compliance_status: complianceStatus,
      local_hires: localHires,
      community_engagement_notes: communityEngagementNotes,
      previous_project_id: previousProjectId,
      benchmark_cost_per_unit: benchmarkCostPerUnit,
      tags,
      critical_path_duration: criticalPathDuration,
      key_milestones: keyMilestones,
      safety_incidents: safetyIncidents,
      incident_notes: incidentNotes,
      bim_file_url: bimFileUrl,
      bim_model_id: bimModelId,
      updated_by: updatedBy,
    };

    try {
      const res = await fetch('/projects/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.error || 'Server error');
      } else {
        alert('Project added successfully');
      }
    } catch (err) {
      alert('Network error');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-box">
        <h2>Add Project</h2>
        <div className="form-header">
          <h2>Add Project</h2>
          <button type="submit" className="save-btn">Save Project</button>
        </div>

        <section>
          <h3>Project information</h3>
          <label>
            Project Name<span className="required">*</span>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Name"
              required
            />
          </label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
          <label>
            Project Number<span className="required">*</span>
            <input
              value={projectNumber}
              onChange={(e) => setProjectNumber(e.target.value)}
              placeholder="Project Number"
              required
            />
          </label>
          <label>
            Category<span className="required">*</span>
            <input
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Category"
              required
            />
          </label>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="planned">Planned</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="on_hold">On Hold</option>
            <option value="canceled">Canceled</option>
          </select>
          <input type="number" value={criticalPathDuration} onChange={(e) => setCriticalPathDuration(e.target.value)} placeholder="Critical Path Duration" />
          <input value={keyMilestones} onChange={(e) => setKeyMilestones(e.target.value)} placeholder="Key Milestones (JSON or text)" />

        </section>
        <section>
          <h3>Client Info</h3>
          <input value={clientName} onChange={(e) => setClientName(e.target.value)} placeholder="Client Name" />
          <input value={projectManager} onChange={(e) => setProjectManager(e.target.value)} placeholder="Project Manager" />
          <input value={address} onChange={(e) => setAddress(e.target.value)} placeholder="Address" />
        </section>
        <section>
          <h3>Budget</h3>
          <input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="Budget" />
          <input type="number" value={originalBudget} onChange={(e) => setOriginalBudget(e.target.value)} placeholder="Original Budget" />
          <input type="number" value={revisedBudget} onChange={(e) => setRevisedBudget(e.target.value)} placeholder="Revised Budget" />
          <input type="number" value={contingencyFund} onChange={(e) => setContingencyFund(e.target.value)} placeholder="Contingency Fund" />
        </section>
        <section>
          <h3>Risk Management</h3>
          <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <textarea value={riskNotes} onChange={(e) => setRiskNotes(e.target.value)} placeholder="Risk Notes" />
          <input value={mapUrl} onChange={(e) => setMapUrl(e.target.value)} placeholder="Map URL" />
          <input type="number" value={latitude} onChange={(e) => setLatitude(e.target.value)} placeholder="Latitude" />
          <input type="number" value={longitude} onChange={(e) => setLongitude(e.target.value)} placeholder="Longitude" />
        </section>
        <section>
          <h3>Media</h3>
          <input value={pictureUrl} onChange={(e) => setPictureUrl(e.target.value)} placeholder="Picture URL" />
          <input value={videoCaptureUrl} onChange={(e) => setVideoCaptureUrl(e.target.value)} placeholder="Video Capture URL" />
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </section>
        <section>
          <h3>Project Details</h3>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Notes" />
          <input value={planRepositoryUrl} onChange={(e) => setPlanRepositoryUrl(e.target.value)} placeholder="Plan Repository URL" />
          <select value={sustainabilityRating} onChange={(e) => setSustainabilityRating(e.target.value)}>
            <option value="">--Sustainability Rating--</option>
            <option value="basic">Basic</option>
            <option value="silver">Silver</option>
            <option value="gold">Gold</option>
            <option value="platinum">Platinum</option>
          </select>
          <textarea value={sustainabilityGoals} onChange={(e) => setSustainabilityGoals(e.target.value)} placeholder="Sustainability Goals" />
          <input value={collaborationUrl} onChange={(e) => setCollaborationUrl(e.target.value)} placeholder="Collaboration URL" />
          <label>
            <input type="checkbox" checked={integrationStatus} onChange={(e) => setIntegrationStatus(e.target.checked)} />
            Integration Status
          </label>
          <input type="date" value={auditDueDate} onChange={(e) => setAuditDueDate(e.target.value)} />
          <select value={complianceStatus} onChange={(e) => setComplianceStatus(e.target.value)}>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="non_compliant">Non-compliant</option>
          </select>
          <input value={bimFileUrl} onChange={(e) => setBimFileUrl(e.target.value)} placeholder="BIM File URL" />
          <input value={bimModelId} onChange={(e) => setBimModelId(e.target.value)} placeholder="BIM Model ID" />

        </section>
        <section>
          <h3>Community Engagement</h3>
          <input type="number" value={localHires} onChange={(e) => setLocalHires(e.target.value)} placeholder="Local Hires" />
          <textarea value={communityEngagementNotes} onChange={(e) => setCommunityEngagementNotes(e.target.value)} placeholder="Community Engagement Notes" />
          <input value={previousProjectId} onChange={(e) => setPreviousProjectId(e.target.value)} placeholder="Previous Project ID" />
          <input type="number" value={benchmarkCostPerUnit} onChange={(e) => setBenchmarkCostPerUnit(e.target.value)} placeholder="Benchmark Cost per Unit" />
          <input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="Tags (JSON or comma-separated)" />
          <input type="number" value={safetyIncidents} onChange={(e) => setSafetyIncidents(e.target.value)} placeholder="Safety Incidents" />
          <textarea value={incidentNotes} onChange={(e) => setIncidentNotes(e.target.value)} placeholder="Incident Notes" />
          <input value={updatedBy} onChange={(e) => setUpdatedBy(e.target.value)} placeholder="Updated By" />
        </section>

      </div>
    </form>
  );
}
