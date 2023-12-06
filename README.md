# Charting a Digital Future

A visualization dashboard that would help us to discover and compare trends on Philippine Digital payment and banking adoption with its peer countries.

The rapid changes brought by technology have taken over several industries, including banking. Digital payments and digital banking are the new trend, and the Philippines is catching up. According to his speech during the GCash Digital Excellence Awards in December 2022, former BSP Governor Felipe M. Medalla mentioned promoting inclusive digital finance as the first objective under the National Strategy for Financial Inclusion 2022–2028. In 2020, the creation of the Digital Payments Transformation Roadmap 2020–2023 was also set out with one of its target goals being onboarding of at least 70.0 percent of Filipino adults to the formal financial system.

While a number of Filipinos are already getting into the digital banking sphere, there are still many Filipinos who either, know about digital banks but are not fully aware of its growth in the country, or also Filipinos who find it harder to open traditional banking accounts but want to explore these digital options, since the BSP also wants to strengthen digital finance for the “underserved and unbanked.” By creating a visualization dashboard that highlights key statistics on the state of digital banking and finance in the Philippines, as well as a visualization on how the country fares against its Asian peers, we may be able to discover and compare trends in this field. As such, having a visualization on the growth of digital banking and finance may be able to encourage Filipinos to start opening digital bank accounts and in turn even further promote financial literacy and inclusion in the country. Banks may also be able to make use of the dashboard to help sell their digital banking services to potential clients.

**[Charting a Digital Future](http://regflores.pythonanywhere.com/)** is a Dash app, created by Group 4 (Cruz, Flores, Pedernal) for the fulfilment of DAT101M Data Visualization. To run the app locally, unzip the files provided and follow steps below:
***

## Dependencies

`Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.`

```bash
pip install dash==2.14.2
pip install dash-bootstrap-components==1.5.0
pip install dash-core-components==2.0.0
pip install dash-html-components==2.0.0
pip install dash-table==5.0.0
pip install numpy==1.24.3
pip install geopandas==0.14.0
pip install pandas==1.5.3
pip install pathlib==1.0.1
pip install plotly==5.9.0
pip install regex==2022.7.9
pip install Pillow==9.4.0
```

***

## Usage


`The directory setup must be:`
```bash
- <local directory path>
     - data/
     - app.py
```

`Using Anaconda Prompt, descend into the local directory:`
```bash
cd <local directory path>
dir
```

`Launch the flask app:`
```bash
python app.py
```

`The expected output is similar to below. Use CTRL+click to open the app on your default web browser:`
```
Dash is running on http://127.0.0.1:8050/
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:8050
Press CTRL+C to quit
```

***

# Authors

For questions, inputs or comments on this app, feel free to reach out to:

- Cruz, Lizelle (lizelle_ann_v_cruz@dlsu.edu.ph)
- Flores, Regina (regina_flores@dlsu.edu.ph)
- Pedernal, Emmanuel (emmanuel_pedernal@dlsu.edu.ph)
