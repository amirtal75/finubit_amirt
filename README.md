## Usage


1. Clone the project
```bash
  git clone https://github.com/barkai36/finubit-observ-lab.git
```
3. Go to project directory
```bash
cd finubit-observ-lab
```
4. Run project
```bash
docker-compose up --build 
```

## Testing
The project will run two services: 'deposit' and 'core'.


The 'deposit' service represent a front-end service to customers.

The 'core' service represent a back-end that is not reached to customer.

The following API requests are available with 'deposit':

http://localhost:5002/deposit
Deposit ammount of money into the account.

Example:
```bash
curl --location 'http://localhost:5002/deposit' \
--header 'Content-Type: application/json' \
--data '{
    "amount":100
}'
```

http://localhost:5002/withdraw
Withdraw amount of money from the account
Example:
```bash
curl --location 'http://localhost:5002/withdraw' \
--header 'Content-Type: application/json' \
--data '{
    "amount":100
}'
```
