import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import json

import datetime
from scipy.stats import gamma, poisson
from functools import reduce

class Site:
   def __init__(self, name, alpha, beta, open_date, close_date, screen_pass, complete):
       self.name = name
       self.alpha = alpha
       self.beta = beta
       self.open = open_date
       self.close = close_date
       self.screen_pass = screen_pass
       self.complete = complete
 
   def __repr__(self):
       return f"Clinical Site class containing {self.name} with alpha={self.alpha}, beta={self.beta}"
 
   def one_sim(self):
       alpha = self.alpha
       beta = self.beta
       n = (self.close - self.open).days
       screen_pass = self.screen_pass
       complete = self.complete
 
       samples = []
       n_pass, n_fail, n_comp, n_death = 0, 0, 0, 0
       for i in range(0,n):
           lam = gamma.rvs(a=alpha, loc=0, scale=beta, size=1)
           X = poisson.rvs(lam, size=1)
 
           X_pass = np.random.binomial(X[0], screen_pass, size=1)
           X_fail = X - X_pass
           n_pass += X_pass
           n_fail += X_fail
 
           X_comp = np.random.binomial(X_pass[0], complete, size=1)
           X_death = X_pass - X_comp
           n_comp += X_comp
           n_death += X_death
 
 
           samples.append((lam[0], X[0], X_pass[0], X_fail[0], X_comp[0], X_death[0]))
 
       samples_df = pd.DataFrame(samples, columns=['lam', 'X', 'X_pass', 'X_fail', 'X_comp', 'X_death'],
                               dtype=float)
 
       samples_df['cum_X'] = samples_df['X'].cumsum()
       samples_df['cum_X_pass'] = samples_df['X_pass'].cumsum()
       samples_df['cum_X_fail'] = samples_df['X_fail'].cumsum()
       samples_df['cum_X_comp'] = samples_df['X_comp'].cumsum()
       samples_df['cum_X_death'] = samples_df['X_death'].cumsum()
 
 
       return samples_df
 
   def cost_fcn(self, samples_df):
       # sample an activation cost from a triangular distribution
       activation = np.random.triangular(5000, 7500, 10000, size=1)
       ps_cost = 50
       s_cost = 100
       sf_cost = 100
       sf_opp_cost = 50
       c_cost =100
       d_cost = 100
       d_opp_cost = 50
 
 
       cost = \
           samples_df['X'] * ps_cost + \
           samples_df['X_pass'] * s_cost + \
           samples_df['X_fail'] * (sf_cost + sf_opp_cost) + \
           samples_df['X_comp'] * c_cost + \
           samples_df['X_death'] * (d_cost + d_opp_cost)
 
       return cost.cumsum().tolist()
 
   def sim_site(self, plot=False) -> None:
       """
       Run 100 simulations from the start date to the end date to model enrollment
       at all stages of the lifecycle.
      
       Output simulations will be of shape (100, close_date-start_date)
       """
 
       pre_screen = []
       screen_pass = []
       screen_fail = []
       complete = []
       death = []
       cost = []
 
       # perform one draw
       n = (self.close - self.open).days
 
       for i in range(0, 100):
           # variation in prior params
           alpha = np.abs(np.random.normal(0.25,0.05))
           beta = np.abs(np.random.normal(0.10, 0.01))
 
 
           samples_df = self.one_sim()
 
           # bootstrap over many draws
           pre_screen.append(samples_df['cum_X'].tolist())
           screen_pass.append(samples_df['cum_X_pass'].tolist())
           screen_fail.append(samples_df['cum_X_fail'].tolist())
           complete.append(samples_df['cum_X_comp'].tolist())
           death.append(samples_df['cum_X_death'].tolist())
          
          
           cost.append(self.cost_fcn(samples_df))
 
       output = dict()
       output['pre_screen'] = pre_screen
       output['screen_pass'] = screen_pass
       output['screen_fail'] = screen_fail
       output['complete'] = complete
       output['death'] = death
       output['cost'] = cost
 
       self.sim_output = output
 
       if plot:
           self.plot_sims()
 
       return None
 
   def process_CIs(self, x_list):
 
       df = pd.DataFrame(x_list)
 
       upper = df.quantile(0.975, axis=0)
       lower = df.quantile(0.025, axis=0)
       med   = df.quantile(0.5, axis=0)
 
       return (lower, med, upper)

   def get_CIs(self):

       CIs = {k:{} for k in self.sim_output}
       # allows for date to be JSON serializable
       # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
       CIs['date_range'] = [t.date().isoformat() for t in self.get_date_range()]

       for k in self.sim_output.keys():
           (lower, med, upper) = self.process_CIs(self.sim_output[k])

           CIs[k]['lower'] = lower.tolist()
           CIs[k]['med'] = med.tolist()
           CIs[k]['upper'] = upper.tolist()

       
       self.flask_CIs = CIs
       return json.dumps(CIs)    
  
   def get_date_range(self):
       # note date range is always going to be 1 longer than the forecasts, since we only forecast for tomorrow onwards
       return pd.date_range(self.open, self.close)[1:]

   def plot_sims(self):
       dates = self.get_date_range()
       fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1,5,sharey=True, figsize=(8,6))
       fig.suptitle('Enrollment Lifecycle')
 
       (lb, m, ub) = self.process_CIs(self.sim_output['pre_screen'])
       ax1.plot(dates, m)
       ax1.fill_between(dates, ub, lb, alpha=0.25)
       ax1.set_title('Pre-Screen')
       ax1.set_ylabel('Number of Subjects')
       ax1.tick_params(axis='x', labelrotation=45)
       ax1.xaxis.set_major_locator(plt.MaxNLocator(4))
 
       (lb, m, ub) = self.process_CIs(self.sim_output['screen_pass'])
       ax2.plot(dates, m)
       ax2.fill_between(dates, ub, lb, alpha=0.25)
       ax2.set_title('Screen Pass')
       ax2.tick_params(axis='x', labelrotation=45)
       ax2.xaxis.set_major_locator(plt.MaxNLocator(4))
 
       (lb, m, ub) = self.process_CIs(self.sim_output['screen_fail'])
       ax3.plot(dates, m)
       ax3.fill_between(dates, ub, lb, alpha=0.25)
       ax3.set_title('Screen Fail')
       ax3.set_xlabel('Normalized Day')
       ax3.tick_params(axis='x', labelrotation=45)
       ax3.xaxis.set_major_locator(plt.MaxNLocator(4))
 
       (lb, m, ub) = self.process_CIs(self.sim_output['complete'])
       ax4.plot(dates, m)
       ax4.fill_between(dates, ub, lb, alpha=0.25)
       ax4.set_title('Completion')
       ax4.tick_params(axis='x', labelrotation=45)
       ax4.xaxis.set_major_locator(plt.MaxNLocator(4))
 
       (lb, m, ub) = self.process_CIs(self.sim_output['death'])
       ax5.plot(dates, m)
       ax5.fill_between(dates, ub, lb, alpha=0.25)
       ax5.set_title('Discontinuated')
       ax5.tick_params(axis='x', labelrotation=45)
       ax5.xaxis.set_major_locator(plt.MaxNLocator(4))
 
       fig, ax = plt.subplots()
 
       output = self.sim_output
       output = output['cost']
 
       # add the site activation once per simulation
       for i in range(0,len(output)):
           row = output[i]
           activation = np.random.triangular(5000, 7500, 10000, size=1)[0]
           activation = np.round(activation, 2)
           row = [x + activation for x in row]
 
           output[i] = row
       cost_df = pd.DataFrame(output)
       #cost_df = pd.DataFrame(self.sim_output['cost'])
       #cost_df = cost_df
       lb = cost_df.quantile(0.025, axis=0)
       m  = cost_df.quantile(0.5, axis=0)
       ub = cost_df.quantile(0.975, axis=0)
       ax.plot(dates, m)
       ax.fill_between(dates, ub, lb, alpha=0.25)
       ax.set_title('Cummulative Cost')
       ax.yaxis.set_major_formatter('${x:1.0f}')
       ax.set_xlabel('Normalized Day')
       ax.tick_params(axis='x', labelrotation=45)
 
       return None
 

