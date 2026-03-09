# Data Visualization MDS/MEI

## First practical work

### Introduction

We want to see how the evolution of the Simpsons' ratings have evolved over the years.

With the provided datasets, you have to create a set of views using Python and Vega-Altair that answer to the
following questions (or can help the users get insights of the data regarding them):

- How have the ratings evolved over time?
- How have the viewers evolved over time?
- Is there a correlation between the gradings and the viewers?
- Are the number of viewers for the episodes related to the weekday they were aired?
- Do the seasons' number of viewers present any relevant pattern?

Some of the questions can be interpreted in slightly different ways that may lead to different charts. You have
to prepare charts to solve all the tasks. And the final outcome, the one that must be implemented in Streamlit,
must be an explanatory visualization that answers all the answers. For this final visualization, that will likely
include multiple views, you have to think of the practical guidelines that we have explained, plus everything
we teach in the theory sessions.

You may add extra questions.

Think carefully the design of all the charts, including the final visualization. Test and redesign.

### Data

Dataset: https://www.kaggle.com/datasets/prashant111/the-simpsons-dataset/data. This Kaggle website
contains a set of files. For the moment, we are interested in the chapters' ratings, that are stored in the CSV
file called simpsons_episodes.csv. Check the files' descriptions to understand what they contain.

You need to clean it and keep relevant information if needed.

### Data processing

Of course, the first step you need to do is cleaning. Our advice is to use Open Refine. But you can do it using
other tools. But take into account that failing to clean properly will lead to problems in visualizations that will
penalize you.

As said, you can process the data using either Open Refine, or another tool. You can also process the data
programmatically. In any case, you need to deliver the clean dataset. And any raw data plus clean data if you
incorporate more information. Independently of the cleaning tool and process, you must describe your
cleaning steps in your Google Colab (Jupyter Notebook) document. If these are using pandas, for example, include the code in the
document. We must be able to reproduce the steps and go from the raw data to the clean version.

### Design and implementation

For each question, a chart (or more than one) needs to be designed and implemented. You may tackle the
problem in different ways: there is not a single solution. You also need to provide a text of a maximum of 200
words per question (and for the final visualization too) where you explain the design decisions and how these
help the users to answer the questions properly. This should include aspects such as: what type of chart did
you select and why, what were the different steps of design process you followed, what changes you applied
to improve legibility, reduce clutter, distinguish elements, how would a person answer the question with your
chart, what other alternatives did not work. Be concise. You do not need to erase the previous steps in design
you followed, they are actually encouraged. But only a final description per task is necessary.

Before you start coding anything, you need to think on what visualizations will be provided. Note that the user
needs to be able to answer the questions above with a single visualization, that will include multiple views.
Consider all sorts of charts that might be useful: line charts, bar charts, maps, heat maps, treemaps… Some
views will contain several variables, so use visual cues, proper palettes to ensure they are understood properly.

A final visualization is also required that includes all questions. In this case, you also have to explain, in a
maximum of 200 words, what changes were made to make charts consistent, aesthetically pleasant, etc. The
final visualization must be then incorporated in a Streamlit application (https://streamlit.io/). You have to teach
yourselves on how to implement applications using Streamlit, which is very easy. You can start checking the
initial videos of this playlist:
https://www.youtube.com/playlist?list=PLtqF5YXg7GLmCvTswG32NqQypOuYkPRUE, or you can start with
some of the videos by Fanilo Andrianasolo: https://www.youtube.com/@andfanilo. He has a subsection for
starters with some interesting videos.

### Delivery instructions

The work can be implemented individually or in pairs. You have to provide the clean data. You have to describe
the cleaning procedure, so that we can generate the clean data from the raw data following your steps. This
description must go in the Colab (Jupyter Notebook) document.

The delivery must consist on a single ZIP file with a name that includes the authors, that contains the datasets
(raw and clean), the Colab (Jupyter Notebook) file(s) (ipnyb), the Python Streamlit application, and optional extra documents if
required. The ZIP, Streamlit, and Colab (Jupyter Notebook) files must be named after the names of the authors. Treat the Colab (Jupyter Notebook)
document as a report, include titles, boldfaces, etc., to make it easier to read.

Upon delivery, an interview with the teacher of your lab will be held to help us understand your development.
Such an interview is compulsory; it is part of the delivery. During the interview, the teacher will ask you
questions about the project, such as design decisions, or implementation details. How you answer those
questions will determine your individual grade. These interviews will happen during a regular lab session, or in
the teacher's office. They will likely be individual, independently of whether the project was done in pairs or
not.

The deadline for the delivery of this lab project is the 1st of April. Delivery through Racó (raco.fib.upc.edu).

### Important remarks

The final grade will take into account the number of variables included in the visualizations (these may include
new calculated variables, such as averages, maxima, minima, etc.). Additionally, we will value the number of
non-trivial tasks (adequately described in the documentation) that can be properly solved with your
visualization tool. In this sense, adding other data sources if suitable will be appreciated.

Don't leave the project for the last day or do the minimum amount of work. In case of doubt, ask whether the
current work is enough or needs more effort.

### This checklist serves as guidance for your delivery

**Global checklist:**

- Name the file after the name(s) of the author(s).
- Include the name(s) of the authors also as the first line in your notebook.
- Include the clean data.
- Compress all files in a single zip (do not use RAR or other formats) file.
- Also include the names of the authors in the notebook (e.g., a text cell showing who authored the
  document) and in the Streamlit app (e.g., in an "About" option).
- Ensure the names of the data files inside the notebook correspond to the ones you deliver.
- Make a single delivery per group.
- Ensure you properly cleaned the data.
- Ensure the code executes without errors: last-minute changes may lead to typos.
- Ensure you include a step-by-step design process (does not need to include all minimal steps, if you
  prefer, but do not forget to include the discussion on why do you change something).
- Do not mix charts with other technologies, everything must be created using altair.
- Ensure they do not include non-properly cleaned data (e.g., N/A or undefined fields).

**Google Colab (Jupyter Notebook) document. For every chart, you must consider:**

- Color blindness (e.g., coding anything just with a red-green palette may be problematic).
- Check the consistency of colors across the whole visualization (same color, same meaning in
  different charts).
- Do not forget to add meaningful titles, labels, messages if necessary...
- When using colors with opacity different from zero, check the interactions with the other elements
  (are they visible?).
- Think whether you need to normalize values.

**For the Streamlit vis:**

- All questions should be solved in a single page (with not much scrolling, e.g., maximum double the
  available screen on a 15" laptop screen).
- The application should run with a simple "streamlit run <application_name>" in any computer,
  everything should be available in the same folder or addressed properly.
- Do not forget to include a final visualization that answers all the questions.
- Align things, be consistent. You can make use of both vertical and horizontal alignments to facilitate
  comparisons.
- Extra questions you answer must also go into the final vis.
- Ensure charts can be visually compared properly (consider changing scales, palettes...)
- Use space cleverly (put related things together and unrelated things far away).
- The higher the number of variables (and questions answered) included, the better.
- If you do not use all your data in your vis, ensure you have filtered it previously, don't force Streamlit
  to execute with data it is not used.
- (For the second lab) Ensure the default values make sense (e.g., if including selections, check that the
  initial configuration of the chart has a default state that is meaningful).
- (For the second lab) Minimize the number of interactions required to solve the problems.
