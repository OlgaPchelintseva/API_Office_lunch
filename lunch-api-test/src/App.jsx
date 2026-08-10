import { useState } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {

  const [responseLog, setResponseLog] = useState('');
  const [username, setUsername] = useState('Sasha');
  const [email, setEmail] = useState('example@ex.com')
  const [creatorId, setCreatorId] = useState(1);
  const [restaurantName, setRestaurantName] = useState('Pizza House');
  const [deadline, setDeadline] = useState('2026-12-31T18:00:00');
  const [sessionId, setSessionId] = useState(1);
  const [newStatus, setNewStatus] = useState('ordered');
  const [itemName, setItemName] = useState('Пепперони');
  const [itemPrice, setItemPrice] = useState(650);
  const [userId, setUserId] = useState(1);
  const [menuItemId, setMenuItemId] = useState(1);
  const [quantity, setQuantity] = useState(2);
  const [orderItemId, setOrderItemId] = useState(1);

  const makeRequest = async(url, method='GET', body=null) => {
    try {
      const options = {
        method,
        headers: {'Content-Type': 'application/json'},
      };
      if (body) options.body = JSON.stringify(body);
      const res = await fetch(`${API_BASE}${url}`, options);
      const data = await res.json();

      setResponseLog(JSON.stringify({
        status: res.status,
        statusText: res.statusText,
        data: data
      }, null, 2));
    } catch (err){
      setResponseLog(JSON.stringify({
        error: err.message
      }, null, 2))
    }
  };

  return (
    <div style={{padding: '20px', fontFamily: 'monospace', maxWidth: '1100px', margin: '0 auto'}}>
      <h1>Тестирование API "Офисный обед"</h1>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
        {/* ЛЕВАЯ КОЛОНКА: управление эндпоинтами */}
        <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
          {/* 1. Пользователи */}
          <fieldset style={{border: '1px solid #ccc', padding: '10px'}}>
            <legend>1. Пользователи (/users)</legend>
            <button onClick={() => makeRequest('/users/')}>
              GET /users
            </button>
            <hr />
            <input 
              placeholder='Username'
              value={username}
              onChange={e => setUsername(e.target.value)} />
            <input 
              placeholder='Email'
              value={email}
              onChange={e => setEmail(e.target.value)} />
            <button onClick={() => makeRequest('/users/', 'POST', {username, email})}>
              POST /users
            </button>
          </fieldset>
          {/* 2. Сессии */}
          <fieldset style={{border: '1px solid #ccc', padding: '10px'}}>
            <legend>2. Сессии (/sessions)</legend>
              <button onClick={() => makeRequest('/sessions/')}>
                GET /sessions
              </button>

              <hr />
              <input 
                type='number'
                placeholder='Creator ID'
                value={creatorId}
                onChange={e => setCreatorId(Number(e.target.value))}
               />
              <input 
                type='text'
                placeholder='Ресторан'
                value={restaurantName}
                onChange={e => setRestaurantName(e.target.value)}
              />
              <input 
                type='text'
                placeholder='Дедлайн'
                value={deadline}
                onChange={e => setDeadline(e.target.value)}
              />
              <button onClick={() => makeRequest('/sessions/', 'POST', {creator_id: creatorId, restaraunt_name: restaurantName, deadline: deadline})}>
                POST /sessions
              </button>

              <hr />
              <input 
                type='number'
                placeholder='Session'
                value={sessionId}
                onChange={e => setSessionId(Number(e.target.value))}
              />
              <button onClick={() => makeRequest(`/sessions/${sessionId}`)}>
                GET /sessions/{'{id}'}
              </button>

              <hr />
              <select 
                value={newStatus}
                onChange={e => setNewStatus(e.target.value)}
              >
                <option value="active">Active</option>
                <option value="ordered">Ordered</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <button onClick={() => makeRequest(`/sessions/${sessionId}/status`, 'PATCH', {status: newStatus})}>
                PATCH /sessions/{'{id}'}/status
              </button>
          </fieldset>
        </div>

        {/* ПРАВАЯ КОЛОНКА: вывод результата запроса */}
        <div>
          <h3>Отыет сервера (JSON Response)</h3>
          <pre style={{backgroundColor: '#1e1e1e', color: '#00ff00', padding: '15px', borderRadius: '5px', maxHeight: '800px', overflow: 'auto'}}>
            {responseLog || '// Нажмите на любую кнопку для выполнения запроса'}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default App
