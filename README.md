# Repo for DS6600 course project

**Core idea:** build a dataset of actors/actresses displaying different emotions

**Tool:** Google Custom Search API

**Constraints:** 

- 100 queries per day
- Max num results per query: 10

**Strategy**

- Create a list/json of all actors/actresses
- Scrape 500 images for each emotion by actors/actresses (3 1/2 days per actor/actress)
- Use Deepface to discard images w/out faces and estimate emotions
- Compare images using SIFT w/ a benchmark from each actor/actress to make sure they are images of them

