console.log("Frontend JS loaded");
const socket = io.connect('http://localhost:5000');
const clearBtn = document.getElementById('clear-btn');
const connectBtn = document.getElementById('connect-btn');
const demoBtn = document.getElementById('demo-btn');
const toggleBtn = document.getElementById('toggle-btn');
const executeBtn = document.getElementById('execute-btn');
const connectionStatus = document.getElementById('connection-status');
const ethBalance = document.getElementById('eth-balance');
const usdbcBalance = document.getElementById('usdbc-balance');
const ethValue = document.getElementById('eth-value');
const ethPrice = document.getElementById('eth-price');
const transactionList = document.getElementById('transaction-list');
const nextExecution = document.getElementById('next-execution');
const lastExecution = document.getElementById('last-execution');
const rebalanceBar = document.getElementById('rebalance-bar');
const walletModal = new bootstrap.Modal('#walletModal');
const agentAddress = document.getElementById('agent-address');
const demoBanner = document.getElementById('demo-banner');

let agentState = {
    status: 'running',
    ethBalance: 0,
    tokenBalance: 0,
    ethPrice: 0,
    agentAddress: null,
    transactions: [],
    nextExecution: '09:00:00',
    lastExecution: null,
    demo_mode: false
};
console.log("Initial agent state:", agentState);
socket.on('connect', () => {
    console.log('Connected to server via Socket.IO');
    connectionStatus.innerHTML = '<i class="fas fa-plug me-1"></i>Connected';
    connectionStatus.classList.remove('status-disconnected', 'status-error');
    connectionStatus.classList.add('status-connected');
    socket.emit('get_state');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    connectionStatus.innerHTML = '<i class="fas fa-plug me-1"></i>Disconnected';
    connectionStatus.classList.remove('status-connected', 'status-error');
    connectionStatus.classList.add('status-disconnected');
});

socket.on('update', (state) => {
    console.log('Received state update:', state);
    agentState = state;
    updateDashboard();
});

socket.on('transaction', (tx) => {
    console.log('New transaction:', tx);
    addTransactionToTable(tx);
    scrollToNewTransaction();
});

socket.on('error', (error) => {
    console.error('Socket error:', error);
    const errorAlert = document.getElementById('error-alert');
    document.getElementById('error-message').textContent = error.message || error;
    errorAlert.classList.remove('d-none');
    
    setTimeout(() => {
        errorAlert.classList.add('d-none');
    }, 5000);
});

connectBtn.addEventListener('click', () => {
    console.log("Connect button clicked");
    window.location.href = '/connect';
});

demoBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    
    try {
        const response = await fetch('/connect_demo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        
        if (data.status === "success") {
            agentState = data.state;
            localStorage.setItem('demoState', JSON.stringify(agentState));
            
            updateDashboard();
        }
    } catch (err) {
        console.error("Demo activation failed:", err);
    }
});

toggleBtn.addEventListener('click', () => {
    console.log("Toggle button clicked");
    fetch('/toggle', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            agentState.status = data.status;
            updateToggleButton();
        })
        .catch(err => console.error("Toggle error:", err));
});

executeBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    
    const response = await fetch('/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    
    if (data.status === "success") {
        agentState.transactions.unshift({
            hash: data.tx_hash,
            description: agentState.demo_mode ? "DEMO: DCA Execution" : "DCA Execution",
            time: new Date().toLocaleTimeString(),
            status: "success"
        });
        
        updateDashboard();
    }
});

function updateDashboard() {
    console.log("Updating dashboard with state:", agentState);
    ethBalance.textContent = agentState.ethBalance?.toFixed(4) || "0.0000";
    usdbcBalance.textContent = agentState.tokenBalance?.toFixed(2) || "0.00";
    ethPrice.textContent = agentState.ethPrice?.toFixed(2) || "0.00";
    const ethValueAmount = (agentState.ethBalance || 0) * (agentState.ethPrice || 0);
    ethValue.textContent = ethValueAmount.toFixed(2);
    if (agentState.agentAddress) {
        connectionStatus.innerHTML = `<i class="fas fa-wallet me-1"></i>Connected`;
        connectionStatus.classList.remove('status-disconnected', 'status-error');
        connectionStatus.classList.add('status-connected');
        if (!document.getElementById('walletModal').classList.contains('show')) {
            agentAddress.value = agentState.agentAddress;
            walletModal.show();
        }
    } else {
        connectionStatus.innerHTML = `<i class="fas fa-unlink me-1"></i>Not Connected`;
        connectionStatus.classList.remove('status-connected', 'status-error');
        connectionStatus.classList.add('status-disconnected');
    }
    if (agentState.demo_mode) {
        demoBanner.classList.remove('d-none');
    } else {
        demoBanner.classList.add('d-none');
    }
    
    updateExecutionTimes();
    updateTransactions();
    updateToggleButton();
    updateRebalanceBar();
    if (agentState.demo_mode && agentState.eth_balance === 0) {
        agentState.eth_balance = 1.0;
        agentState.token_balance = 1800.0;
        agentState.eth_price = 1800.0;
    }
}

function updateToggleButton() {
    if (agentState.status === 'running') {
        toggleBtn.innerHTML = '<i class="fas fa-pause me-2"></i>Pause';
        toggleBtn.classList.remove('btn-danger');
        toggleBtn.classList.add('btn-warning');
    } else {
        toggleBtn.innerHTML = '<i class="fas fa-play me-2"></i>Resume';
        toggleBtn.classList.remove('btn-warning');
        toggleBtn.classList.add('btn-danger');
    }
}

function updateExecutionTimes() {
    nextExecution.textContent = agentState.nextExecution || '--:--:--';
    lastExecution.textContent = agentState.lastExecution || '--:--:--';
}

function updateRebalanceBar() {
    if (!agentState.ethPrice) return;
    
    const ethValue = (agentState.ethBalance || 0) * (agentState.ethPrice || 0);
    const totalValue = ethValue + (agentState.tokenBalance || 0);
    
    if (totalValue > 0) {
        const ethPercentage = (ethValue / totalValue) * 100;
        const usdbcPercentage = 100 - ethPercentage;
        
        rebalanceBar.style.width = `${ethPercentage}%`;
        rebalanceBar.textContent = `${ethPercentage.toFixed(1)}% ETH / ${usdbcPercentage.toFixed(1)}% USDbC`;
    }
}

function updateTransactions() {
    transactionList.innerHTML = '';
    
    if (!agentState.transactions || agentState.transactions.length === 0) {
        transactionList.innerHTML = `
            <tr>
                <td colspan="4" class="text-center py-5">No transactions yet</td>
            </tr>
        `;
        return;
    }
    
    agentState.transactions.slice(-10).reverse().forEach(tx => {
        addTransactionToTable(tx);
    });
}

function addTransactionToTable(tx) {
    const isDemo = tx.description?.includes('DEMO:') || agentState.demo_mode;
    const statusClass = tx.status === 'success' ? 'text-success' : 'text-danger';
    const statusIcon = tx.status === 'success' ? 'fa-check-circle' : 'fa-times-circle';
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${tx.time || ''}</td>
        <td>
            <span class="font-monospace">${tx.hash?.substring(0, 12)}...${tx.hash?.substring(tx.hash.length - 6)}</span>
            ${isDemo ? '<span class="badge bg-info ms-2">Demo</span>' : ''}
        </td>
        <td>${tx.description || ''}</td>
        <td class="${statusClass}">
            <i class="fas ${statusIcon} me-1"></i>${tx.status || 'pending'}
        </td>
    `;
    transactionList.appendChild(row);
}

function scrollToNewTransaction() {
    if (transactionList.firstChild) {
        transactionList.firstChild.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const savedState = localStorage.getItem('demoState');
    if (savedState) {
        agentState = JSON.parse(savedState);
        updateDashboard();
    }
});

clearBtn.addEventListener('click', () => {
    if (confirm("Clear all transactions?")) {
        if (agentState.demo_mode) {
            agentState.transactions = [];
            agentState.ethBalance = 1.0;
            agentState.tokenBalance = 1800.0;
        } else {
            agentState.transactions = [];
        }
        
        updateDashboard();
        localStorage.setItem('demoState', JSON.stringify(agentState));
    }
});