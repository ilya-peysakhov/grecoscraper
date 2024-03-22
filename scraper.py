import streamlit as st
import pandas as pd
pd.options.mode.copy_on_write = True

# from tqdm.notebook import tqdm_notebook
import scrape_ufc_stats_library as LIB
import yaml

st.set_page_config(layout='wide')

st.title('Scraper')

view = st.sidebar.radio('Select View',('Full Scrape','Custom Scrape'))
config = yaml.safe_load(open('scrape_ufc_stats_config.yaml'))

if view=='Full Scrape':
    c1, c2 = st.columns(2)
    
    with c1:
        start = st.button('Start')
    with c2:
        stop = st.button('Stop')
    
    if not start:
        st.stop()
    
    if stop:
        st.stop()
    
    
    
    
    @st.cache_data
    def getEvents():
        events_url = config['completed_events_all_url']
        soup = LIB.get_soup(events_url)
        all_event_details_df = LIB.parse_event_details(soup)
        return all_event_details_df
    
    
    with st.popover("View Events DF"):
        all_event_details_df = getEvents()
        st.dataframe(all_event_details_df,hide_index=True)
    
    
    # for url in tqdm_notebook(list_of_events_urls):
    # for url in list_of_events_urls:
    #     soup = LIB.get_soup(url)
    #     fight_details_df = LIB.parse_fight_details(soup)
    #     all_fight_details_df = pd.concat([all_fight_details_df, fight_details_df])
    
    # Get all fight details in a list comprehension
    @st.cache_data
    def getFD():
        list_of_events_urls = list(all_event_details_df['URL'])
        all_fight_details_df = pd.DataFrame(columns=config['fight_details_column_names'])
        all_fight_details = [LIB.parse_fight_details(LIB.get_soup(url)) for url in list_of_events_urls]
    # Concatenate all fight details dataframes at once
        all_fight_details_df = pd.concat(all_fight_details, ignore_index=True)
        return all_fight_details_df
    
    with st.popover("View Details DF"):
        all_fight_details_df = getFD()
        st.dataframe(all_fight_details_df,hide_index=True)
    
    
    @st.cache_data
    def getResultsStats():
        list_of_fight_details_urls = list(all_fight_details_df['URL'])
        all_fight_results_df = pd.DataFrame(columns=config['fight_results_column_names'])
        all_fight_stats_df = pd.DataFrame(columns=config['fight_stats_column_names'])
    
        for url in list_of_fight_details_urls:
            # get soup
            soup = LIB.get_soup(url)
            # parse fight results and fight stats
            fight_results_df, fight_stats_df = LIB.parse_organise_fight_results_and_stats(
                soup,
                url,
                config['fight_results_column_names'],
                config['totals_column_names'],
                config['significant_strikes_column_names']
                )
            # concat fight results
            all_fight_results_df = pd.concat([all_fight_results_df, fight_results_df])
            # concat fight stats
            all_fight_stats_df = pd.concat([all_fight_stats_df, fight_stats_df])
        return all_fight_results_df,all_fight_stats_df
    
    
    # show all fight results
    with st.popover('View Results DF'):
        otherdata = getResultsStats()
        all_fight_results_df=otherdata[0]
        st.dataframe(all_fight_results_df,hide_index=True)
    # show all fight stats
    with st.popover('View Stats DF'):
        all_fight_stats_df=otherdata[1]
        st.dataframe(all_fight_stats_df,hide_index=True)


elif view=='Custom Scrape':
    all_event_details_df = st.text_input('Fight Card')
    all_event_details_df = pd.Series(all_event_details_df)

    def getFD():
        list_of_events_urls = list(all_event_details_df['URL'])
        all_fight_details_df = pd.DataFrame(columns=config['fight_details_column_names'])
        all_fight_details = [LIB.parse_fight_details(LIB.get_soup(url)) for url in list_of_events_urls]
    # Concatenate all fight details dataframes at once
        all_fight_details_df = pd.concat(all_fight_details, ignore_index=True)
        return all_fight_details_df

    def getcustomStats():
        all_fight_results_df = pd.DataFrame(columns=config['fight_results_column_names'])
        all_fight_stats_df = pd.DataFrame(columns=config['fight_stats_column_names'])
        for url in list_of_fight_details_urls:
            # get soup
            soup = LIB.get_soup(url)
            # parse fight results and fight stats
            fight_results_df, fight_stats_df = LIB.parse_organise_fight_results_and_stats(
                soup,
                url,
                config['fight_results_column_names'],
                config['totals_column_names'],
                config['significant_strikes_column_names']
                )
            # concat fight stats
        all_fight_results_df = pd.concat([all_fight_results_df, fight_results_df])
            # concat fight stats
        all_fight_stats_df = pd.concat([all_fight_stats_df, fight_stats_df])
        return all_fight_results_df,all_fight_stats_df
            
    if st.button('Start'):
        fd = getFD()
        data = getcustomStats()
        st.dataframe(data[0],hide_index=True)
        st.dataframe(data[1],hide_index=True)
