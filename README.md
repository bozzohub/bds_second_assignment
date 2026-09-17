# bds_second_assignment
=======
# When Should I Use Electricity?

A simple Streamlit app that helps households and EV owners decide whether to use electricity now or wait for a cheaper time.

## Question

**If I need to use a certain amount of electricity today, should I use it now or wait for a cheaper period?**

The user selects an electricity market, chooses an everyday use case such as EV charging or a dishwasher, and enters the expected electricity use in kWh.

The app then compares the current wholesale electricity price with the cheapest remaining period of the day.

## Target audience

Households and EV owners with flexible electricity consumption, especially users who can shift activities such as:

- EV charging
- Dishwasher use
- Washing machine use
- Tumble dryer use

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

## Run locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

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
>>>>>>> 3949733 (Initial electricity price Streamlit app)
