#!/usr/bin/env python
# coding: utf-8

# In[1]:


from gurobipy import Model, GRB
import numpy as np

# Create a new model
m = Model("supply_chain_resilience")

# Example: Parameters (normally, these would come from data)
num_products = 3
num_stages = 3
holding_costs = [0.5, 0.6, 0.7]  # Per product
order_costs = [1.0, 1.2, 1.5]    # Per product
demand_forecasts = [100, 150, 200]  # Per product

# Decision Variables
inventory_levels = m.addVars(num_products, num_stages, vtype=GRB.CONTINUOUS, name="inventory")
order_quantities = m.addVars(num_products, vtype=GRB.CONTINUOUS, name="order")

# Objective Function: Minimize total cost
m.setObjective(sum(holding_costs[i] * inventory_levels[i, t] for i in range(num_products) for t in range(num_stages)) +
               sum(order_costs[i] * order_quantities[i] for i in range(num_products)), GRB.MINIMIZE)

# Constraints
# Inventory balance for each product and stage
for i in range(num_products):
    for t in range(num_stages):
        if t == 0:
            m.addConstr(inventory_levels[i, t] == order_quantities[i] - demand_forecasts[i])
        else:
            m.addConstr(inventory_levels[i, t] == inventory_levels[i, t-1] - demand_forecasts[i])

# Demand fulfillment for each product
for i in range(num_products):
    m.addConstr(sum(inventory_levels[i, t] for t in range(num_stages)) >= demand_forecasts[i])

# Solve the model
m.optimize()

# Print the solution
for v in m.getVars():
    print(f'{v.varName}: {v.x}')

# Total cost
print(f'Total Cost: {m.objVal}')


# In[3]:


from gurobipy import Model, GRB

m = Model("supply_chain_resilience")

# Example: Parameters
num_products = 3  # Number of products
num_stages = 3    # Number of stages in the supply chain
holding_costs = [0.5, 0.6, 0.7]  # Holding cost per product
order_costs = [1.0, 1.2, 1.5]    # Ordering cost per product

# Scenario setup
scenarios = {
    'normal': {'demand': [100, 150, 200], 'probability': 0.5},
    'disruption': {'demand': [150, 200, 250], 'probability': 0.5}
}

# First-stage decision variables
inventory_levels = m.addVars(num_products, num_stages, vtype=GRB.CONTINUOUS, name="inventory")
order_quantities = m.addVars(num_products, vtype=GRB.CONTINUOUS, name="order")

# Second-stage decision variables (for each scenario)
additional_orders = m.addVars(num_products, scenarios.keys(), vtype=GRB.CONTINUOUS, name="additional_order")

# Objective Function: Minimize total expected cost
total_cost = sum(holding_costs[i] * inventory_levels[i, t] for i in range(num_products) for t in range(num_stages)) \
             + sum(order_costs[i] * order_quantities[i] for i in range(num_products))

for scenario_name, scenario in scenarios.items():
    scenario_demand = scenario['demand']
    scenario_probability = scenario['probability']
    total_cost += scenario_probability * \
                  (sum(order_costs[i] * additional_orders[i, scenario_name] for i in range(num_products)) \
                   + sum(holding_costs[i] * inventory_levels[i, t] for i in range(num_products) for t in range(num_stages)))

m.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Inventory balance and demand fulfillment (adjust according to scenario demands)
for i in range(num_products):
    for t in range(num_stages):
        m.addConstr(inventory_levels[i, t] == order_quantities[i] - sum(scenarios[s]['demand'][i] * scenarios[s]['probability'] for s in scenarios))

    m.addConstr(sum(inventory_levels[i, t] for t in range(num_stages)) + sum(additional_orders[i, s] for s in scenarios) >= sum(scenarios[s]['demand'][i] * scenarios[s]['probability'] for s in scenarios))

# Solve the model
m.optimize()

# Output results
for v in m.getVars():
    print(f'{v.varName}: {v.x}')
print(f'Total Expected Cost: {m.objVal}')


# In[ ]:





# In[10]:


from gurobipy import *

# Parameters
num_products = 3
num_stages = 3

order_costs = [10, 12, 15]
holding_costs = [1, 2, 3]

# Demand scenarios
demand_scenarios = {
    'scenario1': [[100, 120, 130], [90, 110, 120], [80, 100, 110]],
    'scenario2': [[110, 130, 140], [100, 120, 130], [90, 110, 120]],
    'scenario3': [[120, 140, 150], [110, 130, 140], [100, 120, 130]],
}

# Probability of demand scenarios
demand_scenario_probabilities = [0.3, 0.4, 0.3]

# Disruption scenarios
disruption_scenarios = {
    'scenario1': [0, 0, 0],
    'scenario2': [0, 0, 1],
    'scenario3': [1, 0, 0],
    'scenario4': [1, 0, 1],
}

# Probability of disruption scenarios
disruption_scenario_probabilities = [0.2, 0.1, 0.3, 0.4]

# Model
m = Model()

# Variables
initial_orders = m.addVars(num_products, vtype=GRB.CONTINUOUS, name="InitialOrders")
additional_orders = m.addVars(num_products, num_stages, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="AdditionalOrders")
inventory_levels = m.addVars(num_products, num_stages, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="InventoryLevels")

# Objective: Minimize total cost
total_cost = quicksum(initial_orders[p] * order_costs[p] for p in range(num_products))
total_cost += quicksum(additional_orders[p, t, ds, dp] * order_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(inventory_levels[p, t, ds, dp] * holding_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))

m.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Initial inventory balance
for p in range(num_products):
    for ds in range(len(demand_scenarios)):
        for dp in range(len(disruption_scenarios)):
            m.addConstr(initial_orders[p] + additional_orders[p, 0, ds, dp] - inventory_levels[p, 0, ds, dp] == demand_scenarios['scenario'+str(ds+1)][p][0] * (1 - disruption_scenarios['scenario'+str(dp+1)][0]))

# Inventory balance for subsequent stages
for p in range(num_products):
    for t in range(1, num_stages):
        for ds in range(len(demand_scenarios)):
            for dp in range(len(disruption_scenarios)):
                m.addConstr(inventory_levels[p, t-1, ds, dp] + additional_orders[p, t, ds, dp] - inventory_levels[p, t, ds, dp] == demand_scenarios['scenario'+str(ds+1)][p][t] * (1 - disruption_scenarios['scenario'+str(dp+1)][t]))

# Solve the model
m.optimize()

# Print the results
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    for var in m.getVars():
        print(f"{var.varName}: {var.x}")
    print(f"Total Cost: {m.objVal}")
else:
    print("No optimal solution found.")


# In[11]:


from gurobipy import *

# Parameters
num_products = 3
num_stages = 3

order_costs = [10, 12, 15]
holding_costs = [1, 2, 3]
min_inventory_levels = [30, 40, 50]  # Minimum inventory level requirements for each product

# Demand scenarios
demand_scenarios = {
    'scenario1': [[100, 120, 130], [90, 110, 120], [80, 100, 110]],
    'scenario2': [[110, 130, 140], [100, 120, 130], [90, 110, 120]],
    'scenario3': [[120, 140, 150], [110, 130, 140], [100, 120, 130]],
}

# Probability of demand scenarios
demand_scenario_probabilities = [0.3, 0.4, 0.3]

# Disruption scenarios
disruption_scenarios = {
    'scenario1': [0, 0, 0],
    'scenario2': [0, 0, 1],
    'scenario3': [1, 0, 0],
    'scenario4': [1, 0, 1],
}

# Probability of disruption scenarios
disruption_scenario_probabilities = [0.2, 0.1, 0.3, 0.4]

# Model
m = Model()

# Variables
initial_orders = m.addVars(num_products, vtype=GRB.CONTINUOUS, name="InitialOrders")
additional_orders = m.addVars(num_products, num_stages, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="AdditionalOrders")
inventory_levels = m.addVars(num_products, num_stages, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="InventoryLevels")

# Objective: Minimize total cost
total_cost = quicksum(initial_orders[p] * order_costs[p] for p in range(num_products))
total_cost += quicksum(additional_orders[p, t, ds, dp] * order_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(inventory_levels[p, t, ds, dp] * holding_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))

m.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Inventory balance and minimum inventory level requirements
for p in range(num_products):
    m.addConstr(initial_orders[p] >= min_inventory_levels[p])  # Ensuring minimum initial orders
    for t in range(num_stages):
        for ds in range(len(demand_scenarios)):
            for dp in range(len(disruption_scenarios)):
                demand = demand_scenarios['scenario' + str(ds + 1)][p][t]
                disruption = disruption_scenarios['scenario' + str(dp + 1)][t]
                # Inventory balance constraint
                if t == 0:
                    m.addConstr(initial_orders[p] + additional_orders[p, t, ds, dp] - inventory_levels[p, t, ds, dp] == demand * (1 - disruption))
                else:
                    m.addConstr(inventory_levels[p, t-1, ds, dp] + additional_orders[p, t, ds, dp] - inventory_levels[p, t, ds, dp] == demand * (1 - disruption))
                # Minimum inventory level constraint
                m.addConstr(inventory_levels[p, t, ds, dp] >= min_inventory_levels[p])

# Solve the model
m.optimize()

# Print the results
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    for var in m.getVars():
        print(f"{var.varName}: {var.x}")
    print(f"Total Cost: {m.objVal}")
else:
    print("No optimal solution found.")


# In[17]:


from gurobipy import *

# Parameters
num_products = 3
num_stages = 3
num_suppliers = 2  # Main and backup supplier
num_retailers = 2

order_costs = [[10, 12, 15], [11, 13, 16]]  # Order costs for main and backup suppliers
holding_costs = [1, 2, 3]
min_inventory_levels = [30, 40, 50]

# Adjusted demand scenarios (considering retailers)
demand_scenarios = {
    'scenario1': [[[100, 120, 130], [80, 100, 110]], [[90, 110, 120], [70, 90, 100]]],  # First list for retailer 1, second list for retailer 2
    'scenario2': [[[110, 130, 140], [90, 110, 120]], [[100, 120, 130], [80, 100, 110]]],
    'scenario3': [[[120, 140, 150], [100, 120, 130]], [[110, 130, 140], [90, 110, 120]]],
}
demand_scenario_probabilities = [0.3, 0.4, 0.3]

# Disruption scenarios for suppliers
disruption_scenarios = {
    'scenario1': [0, 0],  # No disruption
    'scenario2': [1, 0],  # Main supplier disrupted
    'scenario3': [0, 1],  # Backup supplier disrupted
}
disruption_scenario_probabilities = [0.5, 0.3, 0.2]

# Model
m = Model()

# Variables
initial_orders = m.addVars(num_products, num_suppliers, vtype=GRB.CONTINUOUS, name="InitialOrders")
additional_orders = m.addVars(num_products, num_stages, num_suppliers, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="AdditionalOrders")
inventory_levels = m.addVars(num_products, num_stages, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="InventoryLevels")

# Objective: Minimize total cost
total_cost = quicksum(initial_orders[p, s] * order_costs[s][p] for p in range(num_products) for s in range(num_suppliers))
total_cost += quicksum(additional_orders[p, t, s, r, ds, dp] * order_costs[s][p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for s in range(num_suppliers) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(inventory_levels[p, t, r, ds, dp] * holding_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))

m.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
for p in range(num_products):
    for s in range(num_suppliers):
        for dp in range(len(disruption_scenarios)):
            m.addConstr(initial_orders[p, s] >= min_inventory_levels[p] * (1 - disruption_scenarios['scenario' + str(dp + 1)][s]))

    for t in range(num_stages):
        for ds in range(len(demand_scenarios)):
            scenario = 'scenario' + str(ds + 1)
            for r in range(num_retailers):
                for dp in range(len(disruption_scenarios)):
                    # Diagnostics: Check if indices are within the range
                    if p >= len(demand_scenarios[scenario][r]) or t >= len(demand_scenarios[scenario][r][p]):
                        print(f"Index out of range: scenario={scenario}, retailer={r}, product={p}, stage={t}")
                        continue

                    # Correctly access the demand for each retailer, product, stage, and demand scenario
                    demand = demand_scenarios[scenario][r][p][t]
                    # Inventory balance constraint
                    if t == 0:
                        m.addConstr(quicksum(initial_orders[p, s] for s in range(num_suppliers)) + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    else:
                        m.addConstr(inventory_levels[p, t-1, r, ds, dp] + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    # Minimum inventory level constraint
                    m.addConstr(inventory_levels[p, t, r, ds, dp] >= min_inventory_levels[p])

# Solve the model
m.optimize()

# Print the results
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    for var in m.getVars():
        print(f"{var.varName}: {var.x}")
    print(f"Total Cost: {m.objVal}")
else:
    print("No optimal solution found.")


# In[18]:


from gurobipy import *

# Parameters
num_products = 3
num_stages = 3
num_suppliers = 2  # Main and backup supplier
num_retailers = 2

order_costs = [[10, 12, 15], [11, 13, 16]]  # Order costs for main and backup suppliers
holding_costs = [1, 2, 3]
min_inventory_levels = [30, 40, 50]

# Revised demand scenarios
demand_scenarios = {
    'scenario1': [
        [[100, 110, 120], [90, 100, 110], [80, 90, 100]],  # Retailer 1
        [[95, 105, 115], [85, 95, 105], [75, 85, 95]]      # Retailer 2
    ],
    'scenario2': [
        [[110, 120, 130], [100, 110, 120], [90, 100, 110]],
        [[105, 115, 125], [95, 105, 115], [85, 95, 105]]
    ],
    'scenario3': [
        [[120, 130, 140], [110, 120, 130], [100, 110, 120]],
        [[115, 125, 135], [105, 115, 125], [95, 105, 115]]
    ],
}
demand_scenario_probabilities = [0.3, 0.4, 0.3]

# Disruption scenarios for suppliers
disruption_scenarios = {
    'scenario1': [0, 0],  # No disruption
    'scenario2': [1, 0],  # Main supplier disrupted
    'scenario3': [0, 1],  # Backup supplier disrupted
}
disruption_scenario_probabilities = [0.5, 0.3, 0.2]

# Model
m = Model()

# Variables
initial_orders = m.addVars(num_products, num_suppliers, vtype=GRB.CONTINUOUS, name="InitialOrders")
additional_orders = m.addVars(num_products, num_stages, num_suppliers, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="AdditionalOrders")
inventory_levels = m.addVars(num_products, num_stages, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="InventoryLevels")

# Objective: Minimize total cost
total_cost = quicksum(initial_orders[p, s] * order_costs[s][p] for p in range(num_products) for s in range(num_suppliers))
total_cost += quicksum(additional_orders[p, t, s, r, ds, dp] * order_costs[s][p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for s in range(num_suppliers) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(inventory_levels[p, t, r, ds, dp] * holding_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))

m.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
for p in range(num_products):
    for s in range(num_suppliers):
        for dp in range(len(disruption_scenarios)):
            m.addConstr(initial_orders[p, s] >= min_inventory_levels[p] * (1 - disruption_scenarios['scenario' + str(dp + 1)][s]))

    for t in range(num_stages):
        for ds in range(len(demand_scenarios)):
            scenario = 'scenario' + str(ds + 1)
            for r in range(num_retailers):
                for dp in range(len(disruption_scenarios)):
                    demand = demand_scenarios[scenario][r][p][t]
                    # Inventory balance constraint
                    if t == 0:
                        m.addConstr(quicksum(initial_orders[p, s] for s in range(num_suppliers)) + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    else:
                        m.addConstr(inventory_levels[p, t-1, r, ds, dp] + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    # Minimum inventory level constraint
                    m.addConstr(inventory_levels[p, t, r, ds, dp] >= min_inventory_levels[p])

# Solve the model
m.optimize()

# Print the results
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    for var in m.getVars():
        print(f"{var.varName}: {var.x}")
    print(f"Total Cost: {m.objVal}")
else:
    print("No optimal solution found.")


# In[ ]:


#Model With One objective


# In[20]:


from gurobipy import *
import random

# Parameters
num_products = 3
num_stages = 3
num_suppliers = 2  # Main and backup supplier
num_retailers = 2
num_distribution_centers = 2

# Synthetic Data Generation
order_costs = [[10 + random.random(), 12 + random.random(), 15 + random.random()] for _ in range(num_suppliers)]  # Slightly varied order costs
holding_costs = [1, 2, 3]
min_inventory_levels = [30, 40, 50]
distribution_center_capacity = [500, 600]  # Capacity for each distribution center
lead_times = [[random.randint(1, 5) for _ in range(num_suppliers)] for _ in range(num_distribution_centers)]  # Lead times in days

# Demand scenarios - Simplified for illustration
demand_scenarios = {
    'scenario1': [
        [[100, 110, 120], [90, 100, 110], [80, 90, 100]], 
        [[95, 105, 115], [85, 95, 105], [75, 85, 95]]
    ],
    'scenario2': [
        [[110, 120, 130], [100, 110, 120], [90, 100, 110]],
        [[105, 115, 125], [95, 105, 115], [85, 95, 105]]
    ]
}
demand_scenario_probabilities = [0.5, 0.5]

# Disruption scenarios - Simplified for illustration
disruption_scenarios = {
    'scenario1': [0, 0],  # No disruption
    'scenario2': [1, 0],  # Main supplier disrupted
}
disruption_scenario_probabilities = [0.5, 0.5]

# Model
m = Model()

# Variables
# Adding variables for distribution centers
dc_inventory = m.addVars(num_distribution_centers, num_products, vtype=GRB.CONTINUOUS, name="DCInventory")
initial_orders = m.addVars(num_products, num_suppliers, vtype=GRB.CONTINUOUS, name="InitialOrders")
additional_orders = m.addVars(num_products, num_stages, num_suppliers, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="AdditionalOrders")
inventory_levels = m.addVars(num_products, num_stages, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="InventoryLevels")

# Objective: Minimize total cost
total_cost = quicksum(initial_orders[p, s] * order_costs[s][p] for p in range(num_products) for s in range(num_suppliers))
total_cost += quicksum(additional_orders[p, t, s, r, ds, dp] * order_costs[s][p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for s in range(num_suppliers) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(inventory_levels[p, t, r, ds, dp] * holding_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(dc_inventory[d, p] * holding_costs[p] for d in range(num_distribution_centers) for p in range(num_products))

m.setObjective(total_cost, GRB.MINIMIZE)

# Constraints
# Capacity constraints for distribution centers
for d in range(num_distribution_centers):
    m.addConstr(quicksum(dc_inventory[d, p] for p in range(num_products)) <= distribution_center_capacity[d], f"CapacityDC_{d}")

# Inventory balance and minimum inventory level constraints
for p in range(num_products):
    for s in range(num_suppliers):
        for dp in range(len(disruption_scenarios)):
            m.addConstr(initial_orders[p, s] >= min_inventory_levels[p] * (1 - disruption_scenarios['scenario' + str(dp + 1)][s]))

    for t in range(num_stages):
        for ds in range(len(demand_scenarios)):
            scenario = 'scenario' + str(ds + 1)
            for r in range(num_retailers):
                for dp in range(len(disruption_scenarios)):
                    demand = demand_scenarios[scenario][r][p][t]
                    # Inventory balance constraint
                    if t == 0:
                        m.addConstr(quicksum(initial_orders[p, s] for s in range(num_suppliers)) + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    else:
                        m.addConstr(inventory_levels[p, t-1, r, ds, dp] + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    # Minimum inventory level constraint
                    m.addConstr(inventory_levels[p, t, r, ds, dp] >= min_inventory_levels[p])

# Solve the model
m.optimize()

# Print the results
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    for var in m.getVars():
        print(f"{var.varName}: {var.x}")
    print(f"Total Cost: {m.objVal}")
else:
    print("No optimal solution found.")


# In[4]:


from gurobipy import *
import random

# Parameters
num_products = 3
num_stages = 3
num_suppliers = 2
num_retailers = 2
num_distribution_centers = 2

# Synthetic Data Generation
order_costs = [[10 + random.random(), 12 + random.random(), 15 + random.random()] for _ in range(num_suppliers)]
holding_costs = [1, 2, 3]
carbon_emission_factors = [0.5, 0.7, 0.6]  # Carbon emission factor per product
min_inventory_levels = [30, 40, 50]
distribution_center_capacity = [500, 600]

# Dynamic Demand Scenarios
demand_scenarios = {
    'scenario1': [
        [[100 + t*5, 110 + t*5, 120 + t*5] for t in range(num_stages)], 
        [[95 + t*5, 105 + t*5, 115 + t*5] for t in range(num_stages)]
    ],
    'scenario2': [
        [[110 + t*5, 120 + t*5, 130 + t*5] for t in range(num_stages)],
        [[105 + t*5, 115 + t*5, 125 + t*5] for t in range(num_stages)]
    ]
}
demand_scenario_probabilities = [0.5, 0.5]

# Disruption scenarios
disruption_scenarios = {
    'scenario1': [0, 0],
    'scenario2': [1, 0],
}
disruption_scenario_probabilities = [0.5, 0.5]

# Model
m = Model()

# Variables
dc_inventory = m.addVars(num_distribution_centers, num_products, vtype=GRB.CONTINUOUS, name="DCInventory")
initial_orders = m.addVars(num_products, num_suppliers, vtype=GRB.CONTINUOUS, name="InitialOrders")
additional_orders = m.addVars(num_products, num_stages, num_suppliers, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="AdditionalOrders")
inventory_levels = m.addVars(num_products, num_stages, num_retailers, len(demand_scenarios), len(disruption_scenarios), vtype=GRB.CONTINUOUS, name="InventoryLevels")

# Objective: Minimize total cost and carbon emissions
total_cost = quicksum(initial_orders[p, s] * order_costs[s][p] for p in range(num_products) for s in range(num_suppliers))
total_cost += quicksum(additional_orders[p, t, s, r, ds, dp] * order_costs[s][p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for s in range(num_suppliers) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(inventory_levels[p, t, r, ds, dp] * holding_costs[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))
total_cost += quicksum(dc_inventory[d, p] * holding_costs[p] for d in range(num_distribution_centers) for p in range(num_products))

carbon_emissions = quicksum(dc_inventory[d, p] * carbon_emission_factors[p] for d in range(num_distribution_centers) for p in range(num_products))
carbon_emissions += quicksum(additional_orders[p, t, s, r, ds, dp] * carbon_emission_factors[p] * demand_scenario_probabilities[ds] * disruption_scenario_probabilities[dp] for p in range(num_products) for t in range(num_stages) for s in range(num_suppliers) for r in range(num_retailers) for ds in range(len(demand_scenarios)) for dp in range(len(disruption_scenarios)))

# Multi-objective
m.ModelSense = GRB.MINIMIZE
m.setObjectiveN(total_cost, 0, priority=1)
m.setObjectiveN(carbon_emissions, 1, priority=0).

# Constraints
# Capacity constraints for distribution centers
for d in range(num_distribution_centers):
    m.addConstr(quicksum(dc_inventory[d, p] for p in range(num_products)) <= distribution_center_capacity[d], f"CapacityDC_{d}")

# Inventory balance and minimum inventory level constraints
for p in range(num_products):
    for s in range(num_suppliers):
        for dp in range(len(disruption_scenarios)):
            m.addConstr(initial_orders[p, s] >= min_inventory_levels[p] * (1 - disruption_scenarios['scenario' + str(dp + 1)][s]))

    for t in range(num_stages):
        for ds in range(len(demand_scenarios)):
            scenario = 'scenario' + str(ds + 1)
            for r in range(num_retailers):
                for dp in range(len(disruption_scenarios)):
                    demand = demand_scenarios[scenario][r][p][t]
                    # Inventory balance constraint
                    if t == 0:
                        m.addConstr(quicksum(initial_orders[p, s] for s in range(num_suppliers)) + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    else:
                        m.addConstr(inventory_levels[p, t-1, r, ds, dp] + quicksum(additional_orders[p, t, s, r, ds, dp] for s in range(num_suppliers)) - inventory_levels[p, t, r, ds, dp] == demand)
                    # Minimum inventory level constraint
                    m.addConstr(inventory_levels[p, t, r, ds, dp] >= min_inventory_levels[p])


m.optimize()

# Print the results
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    for var in m.getVars():
        print(f"{var.varName}: {var.x}")
    print(f"Total Cost: {m.objVal}")
    print(f"Total Carbon Emissions: {carbon_emissions.getValue()}")
else:
    print("No optimal solution found.")


# In[ ]:




