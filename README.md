# bds_second_assignment
# When Should I Use Electricity?
 
A simple Streamlit app that helps households and EV owners decide whether to use electricity now or wait for a cheaper time.
 
## Question
 
**If I need to use a certain amount of electricity today, should I use it now or wait for a cheaper period?**
 
The user selects an electricity market, chooses an everyday use case such as EV charging or a dishwasher, and enters the expected electricity use in kWh.
 
The app then compares the current wholesale electricity price with the cheapest remaining period of the day.
 
## Target audience
The target audience for this application is an average household that owns some of the larger electrical appliances, such as a dishwasher, washing machine, and tumble dryer.
 
Furthermore, the application is also aimed at the growing number of people who own an electric vehicle.
 
Through this application and the API we have found, we want to create opportunities for people to plan their electricity consumption based on when electricity prices are lower.
 
We believe this will be of interest to users of the application because it gives them the opportunity to save a significant amount of money by, for example, waiting one or two hours before using an appliance or charging their electric vehicle. Alternatively, they can plan their electricity consumption around the times when electricity prices are at their lowest.
 
 
## Data
 
The app uses day-ahead wholesale electricity prices from the Energy-Charts API.
 
Prices are supplied in EUR/MWh and converted to EUR/kWh for the household cost estimate.
 
## Main features
 
- Select an electricity market
- Select an everyday electricity use case
- Enter expected electricity use in kWh
- See the current wholesale electricity price
- Estimate the wholesale cost of using that energy now
- Find the cheapest remaining pricing interval today
- Estimate the potential saving from waiting
- View today's electricity-price curve
 
## Limitation
 
The estimated cost represents only the wholesale electricity component. It does not include grid tariffs, taxes, VAT, supplier charges, or the details of a household electricity contract.
 
 
## AI and tools used
 
- **ChatGPT**: used to help develop and debug the Python/Streamlit code, structure the app, and improve explanations and presentation.
- **Visual Studio Code**: used to edit and run the application locally.
- **GitHub**: used for version control and repository hosting.
- **Streamlit Community Cloud**: used to deploy the live application.
- **Energy-Charts API**: used as the free live-data source.
 
## Files
 
- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies
- `README.md` — project description
