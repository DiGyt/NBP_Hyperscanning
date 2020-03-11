# This is the README to the hyperscanning experiment
## The Data is formatted in Brain Imaging Data Structure (BIDS), using MNE-Python Toolbox

### Experiment Design and Procedure

In the current EEG-hyperscanning study, we simultaneuously recorded brain activity from pairs of participants via EEG while they were performing a joint motor-task. In greater detail, we employed a finger tapping task in which participants had to synchronize their taps within a given period of 9 taps (through pressing a button with the index finger (each participant), thereby eliciting a unique sound that could be heard by both participants; identical as described in [[1]](https://academic.oup.com/scan/article/12/4/662/2948768)). In our experiment, participants were not allowed to interact in any other way than aforementioned. Therefore, they were seated next to each other in a room with a divider between them to prevent them from seeing- and visually interacting with each other. To eliminate auditory input other than the tapping sound, they wore noise cancelling head-phones and ear-muffs. Each participant was facing his/her own screen which displayed stimuli like trial-onset/end cues, brakes, etc.


[[1]](https://academic.oup.com/scan/article/12/4/662/2948768) Novembre, G., Knoblich, G., Dunne, L., & Keller, P. E. (2017). Interpersonal synchrony enhanced through 20 Hz phase-coupled dual brain stimulation. Social cognitive and affective neuroscience, 12(4), 662-670.

### Terminology

Terminology that will be used in the following:

**Subject-pair (sub)** = human-human pair from which data is being acquired  
**Participant**	= Individual human being (2 participants form a subject-pair)  
**Visit**		= a non-intermittent period in which the participant is at the location the experiment takes place  
**Session (ses)**	= Usually: a non-intermittent period in which the participant is wearing the EEG cap.
		  In this case, however, session nr. equals to participant nr. of a subject-pair
		  (e.g. 'sub-202_ses-01' would refer to participant nr. 1 from subject-pair 202)  
**Run**		= a non-intermittent period in which data for the participant(s) is continuously being acquired  
**Task**		= instructions (and corresponding stimulus material) that is performed by the subject-pair  
**Responses**	= recorded behaviour of the participant(s) in relation to the task and/or stimulus  

### Folder Structure example:

|**mne_data**  
|README.md  
|sourcedata  
|--- sub-202  
|------ eeg  
|--------- sub-202-task-hyper_eeg.fif  
|--------- sub-202-task-hyper_eeg-1.fif  
|rawdata  
|--- README.md
|--- participants.tsv  
|--- participants.json  
|--- dataset_description.json  
|--- sub-202  
|----- ses-01  
|-------- sub-202_ses-01_scans.tsv  
|-------- eeg  
|----------- sub-202_ses-01_task-hyper_events.tsv  
|----------- sub-202_ses-01_task-hyper_eeg.json  
|----------- sub-202_ses-01_task-hyper_channels.tsv  
|----------- sub-202_ses-01_task-hyper_eeg.eeg  
|----------- sub-202_ses-01_task-hyper_eeg.vhdr  
|----------- sub-202_ses-01_task-hyper_eeg.vmrk  
|----- ses-02  
|-------- sub-202_ses-02_scans.tsv  
|-------- eeg  
|----------- sub-202_ses-02_task-hyper_events.tsv  
|----------- sub-202_ses-02_task-hyper_eeg.json  
|----------- sub-202_ses-02_task-hyper_channels.tsv  
|----------- sub-202_ses-02_task-hyper_eeg.eeg  
|----------- sub-202_ses-02_task-hyper_eeg.vhdr  
|----------- sub-202_ses-02_task-hyper_eeg.vmrk  
|derivatives  
|--- README.md  




### ToDo:

