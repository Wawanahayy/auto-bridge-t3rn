from web3 import Web3
import time

# URL RPC dan alamat kontrak untuk masing-masing jaringan
rpc_urls = {
    'Optimism': 'https://sepolia.optimism.io/rpc',
    'Blast': 'https://sepolia.blast.io/'
}

contract_addresses = {
    'Optimism': '0xF221750e52aA080835d2957F2Eed0d5d7dDD8C38',
    'Blast': '0x1D5FD4ed9bDdCCF5A74718B556E9d15743cB26A2'
}

# Private key dan alamat wallet (ubah ini dengan data Anda)
private_keys = {
    'Optimism': '0x_Private_Key',
    'Blast': '0x_Private_Key'
}

# Alamat wallet tujuan di setiap jaringan
destination_address = 'YOUR ADDRESS'

chain_ids = {
    'Optimism': 11155420,
    'Blast': 168587773
}


# Inisialisasi Web3 untuk setiap jaringan
web3_instances = {}
accounts = {}

for network, url in rpc_urls.items():
    web3 = Web3(Web3.HTTPProvider(url))
    web3_instances[network] = web3
    # Impor akun dari private key
    private_key = private_keys[network]
    account = web3.eth.account.from_key(private_key)
    accounts[network] = account

def check_connection():
    for network, web3 in web3_instances.items():
        if web3.is_connected():
            print(f"Koneksi ke {network} berhasil!")
        else:
            print(f"Gagal terhubung ke {network}.")

def bridge_tokens(network_from, network_to, amount, times):
    web3_from = web3_instances[network_from]
    web3_to = web3_instances[network_to]
    account_from = accounts[network_from]
    contract_address = contract_addresses[network_from]
    
    balance = web3_from.eth.get_balance(account_from.address)
    gas_price = web3_from.eth.gas_price
    gas_limit = 2000000  # Sesuaikan jika perlu
    total_cost = gas_price * gas_limit + web3_from.to_wei(amount, 'ether')

    for _ in range(times):
        nonce = web3_from.eth.get_transaction_count(account_from.address)
        tx = {
            'nonce': nonce,
            'to': contract_address,
            'value': web3_from.to_wei(amount, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_ids[network_from]
        }
    
    if balance < total_cost:
        print(f"Saldo tidak cukup untuk bridging. Saldo: {web3_from.from_wei(balance, 'ether')} ETH, Total biaya: {web3_from.from_wei(total_cost, 'ether')} ETH")
        return
    
    print(f"Memulai bridging dari {network_from} ke {network_to} sebanyak {times} kali dengan jumlah {amount} token.")
    
    for _ in range(times):
        nonce = web3_from.eth.get_transaction_count(account_from.address)
        tx = {
            'nonce': nonce,
            'to': contract_address,
            'value': web3_from.to_wei(amount, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_ids[network_from]
        }
        signed_tx = web3_from.eth.account.sign_transaction(tx, private_keys[network_from])
        tx_hash = web3_from.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash = web3_from.to_hex(tx_hash)
        
        print(f"Bridging {amount} token dari {network_from} ke {network_to} ke alamat {destination_address}...")
        
        # Tunggu hingga transaksi terkonfirmasi
        receipt = web3_from.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaksi bridging berhasil! Hash transaksi: {tx_hash}")

def get_network_choice(prompt):
    print(prompt)
    for idx, network in enumerate(rpc_urls.keys(), 1):
        print(f"{idx}. {network}")
    choice = int(input("Pilih nomor jaringan: "))
    networks = list(rpc_urls.keys())
    if 1 <= choice <= len(networks):
        return networks[choice - 1]
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")
        return get_network_choice(prompt)

if __name__ == "__main__":
    check_connection()

    network_from = get_network_choice('Dari jaringan mana Anda ingin melakukan bridging?')
    network_to = get_network_choice('Ke jaringan mana Anda ingin melakukan bridging?')
    amount = float(input('Berapa banyak token yang ingin di-bridge? '))
    times = int(input('Berapa kali ingin melakukan bridging? '))

    bridge_tokens(network_from, network_to, amount, times)
