const { useState, useEffect } = React;

const modelConfigs = {
  cwpackage: {
    list: '/cw-packages/list',
    create: '/cw-packages/create',
    update: '/cw-packages/update/',
    remove: '/cw-packages/delete/',
    fields: ['project_id', 'code', 'name', 'unit']
  },
  equipment: {
    list: '/equipment/list',
    create: '/equipment/create',
    update: '/equipment/update/',
    remove: '/equipment/delete/',
    fields: ['name','serial_number','maintenance_status']
  },
  material: {
    list: '/materials/list',
    create: '/materials/create',
    update: '/materials/update/',
    remove: '/materials/delete/',
    fields: ['name','unit','cost_per_unit']
  },
  projectActivityCode: {
    list: '/activity-codes/get_activity_codes',
    create: '/activity-codes/add',
    update: '/activity-codes/update/',
    remove: '/activity-codes/delete/',
    fields: ['code','description']
  },
  purchaseOrder: {
    list: '/purchase-orders/list',
    create: '/purchase-orders/create',
    update: '/purchase-orders/update/',
    remove: '/purchase-orders/delete/',
    fields: ['order_number','vendor']
  },
  subcontractor: {
    list: '/subcontractors/list',
    create: '/subcontractors/add',
    update: '/subcontractors/update/',
    remove: '/subcontractors/delete/',
    fields: ['name','task','contractType']
  },
  workOrder: {
    list: '/work-orders/list',
    create: '/work-orders/add',
    update: '/work-orders/update/',
    remove: '/work-orders/delete/',
    fields: ['order_number','description']
  },
  worker: {
    list: '/workers/list',
    create: '/workers/add-worker',
    update: '/workers/update/',
    remove: '/workers/delete/',
    fields: ['workerName','role']
  }
};

function CrudTable({ model }) {
  const config = modelConfigs[model];
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({});

  const fetchItems = () => {
    axios.get(config.list)
      .then(res => {
        setItems(res.data[model] || res.data.items || []);
      })
      .catch(err => console.error(err));
  };

  useEffect(fetchItems, []);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    axios.post(config.create, form)
      .then(() => { setForm({}); fetchItems(); })
      .catch(err => console.error(err));
  };

  const handleDelete = id => {
    axios.delete(config.remove + id)
      .then(fetchItems)
      .catch(err => console.error(err));
  };

  return (
    <div className="admin-section">
      <h3>{model}</h3>
      <form onSubmit={handleSubmit}>
        {config.fields.map(f => (
          <input key={f} name={f} placeholder={f} value={form[f] || ''} onChange={handleChange} />
        ))}
        <button type="submit">Add</button>
      </form>
      <table>
        <thead>
          <tr>
            {config.fields.map(f => <th key={f}>{f}</th>)}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={idx}>
              {config.fields.map(f => <td key={f}>{item[f]}</td>)}
              <td>
                <button onClick={() => handleDelete(item.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AdminApp() {
  const models = Object.keys(modelConfigs);
  return (
    <div>
      {models.map(m => <CrudTable key={m} model={m} />)}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('admin-root')).render(<AdminApp />);