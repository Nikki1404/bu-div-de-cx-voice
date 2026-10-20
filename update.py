
VOXPROFILE 

Per-file results (age bucket must exactly match the ground-truth decade):
File                               Age GT     Age pred   API bucket Gender GT  Gender pred       RTT   Server Result
01_000030.v2.vad.wav               thirties   20s        20-30      female     female         6.337s   4.803s age:MISS gender:OK
02_000021.v2.vad.wav               ERROR: HTTP 400: Audio contains insufficient speech/audio energy.
03_000015.v2.vad.wav               thirties   20s        20-30      female     female         0.833s   0.043s age:MISS gender:OK
04_000026.v2.vad.wav               thirties   20s        20-30      female     female         0.863s   0.036s age:MISS gender:OK
05_000031.v2.vad.wav               thirties   30s        30-40      female     female         0.656s   0.036s age:OK gender:OK
06_000027.v2.vad.wav               ERROR: HTTP 400: Audio must be at least 3 seconds.
07_000000.v2.vad.wav               thirties   20s        20-30      female     female         0.638s   0.034s age:MISS gender:OK
08_000012.v2.vad.wav               thirties   20s        20-30      female     female         0.655s   0.036s age:MISS gender:OK
09_000005.v2.vad.wav               thirties   20s        20-30      female     male           0.587s   0.035s age:MISS gender:MISS
10_000014.v2.vad.wav               thirties   20s        20-30      female     female         0.890s   0.035s age:MISS gender:OK
11_000004.v2.vad.wav               thirties   40s        40-50      female     female         0.914s   0.036s age:MISS gender:OK
12_000010.v2.vad.wav               thirties   20s        20-30      female     female         0.646s   0.051s age:MISS gender:OK
13_000002.v2.vad.wav               thirties   30s        30-40      female     female         0.668s   0.036s age:OK gender:OK
14_000022.v2.vad.wav               thirties   30s        30-40      female     female         0.632s   0.035s age:OK gender:OK
15_000020.v2.vad.wav               thirties   30s        30-40      female     female         0.644s   0.036s age:OK gender:OK
16_000023.v2.vad.wav               thirties   50s        50-60      female     female         0.646s   0.038s age:MISS gender:OK
17_000016.v2.vad.wav               thirties   30s        30-40      female     female         0.621s   0.035s age:OK gender:OK
18_000029.v2.vad.wav               ERROR: HTTP 400: Audio must be at least 3 seconds.
19_000001.v2.vad.wav               thirties   20s        20-30      female     female         0.685s   0.036s age:MISS gender:OK
20_000007.v2.vad.wav               ERROR: HTTP 400: Audio must be at least 3 seconds.


Audeering-

Per-file results (age bucket must exactly match the ground-truth decade):
File                               Age GT     Age pred   API bucket Gender GT  Gender pred       RTT   Server Result
01_000030.v2.vad.wav               thirties   50s        50-60      female     female         0.886s   0.023s age:MISS gender:OK
02_000021.v2.vad.wav               ERROR: HTTP 400: Audio contains insufficient speech/audio energy.
03_000015.v2.vad.wav               thirties   50s        50-60      female     female         0.745s   0.030s age:MISS gender:OK
04_000026.v2.vad.wav               thirties   20s        20-30      female     female         0.654s   0.029s age:MISS gender:OK
05_000031.v2.vad.wav               thirties   50s        50-60      female     female         0.696s   0.028s age:MISS gender:OK
06_000027.v2.vad.wav               ERROR: HTTP 400: Audio must be at least 3 seconds.
07_000000.v2.vad.wav               thirties   40s        40-50      female     female         0.579s   0.025s age:MISS gender:OK
08_000012.v2.vad.wav               thirties   40s        40-50      female     female         0.656s   0.029s age:MISS gender:OK
09_000005.v2.vad.wav               thirties   30s        30-40      female     male           0.567s   0.023s age:OK gender:MISS
10_000014.v2.vad.wav               thirties   40s        40-50      female     female         0.643s   0.030s age:MISS gender:OK
11_000004.v2.vad.wav               thirties   60s        60-70      female     female         0.672s   0.029s age:MISS gender:OK
12_000010.v2.vad.wav               thirties   30s        30-40      female     female         0.615s   0.031s age:OK gender:OK
13_000002.v2.vad.wav               thirties   50s        50-60      female     female         0.622s   0.030s age:MISS gender:OK
14_000022.v2.vad.wav               thirties   40s        40-50      female     female         0.618s   0.029s age:MISS gender:OK
15_000020.v2.vad.wav               thirties   50s        50-60      female     female         0.659s   0.029s age:MISS gender:OK
16_000023.v2.vad.wav               thirties   60s        60-70      female     female         0.628s   0.029s age:MISS gender:OK
17_000016.v2.vad.wav               thirties   50s        50-60      female     female         0.621s   0.029s age:MISS gender:OK
18_000029.v2.vad.wav               ERROR: HTTP 400: Audio must be at least 3 seconds.
19_000001.v2.vad.wav               thirties   50s        50-60      female     female         0.624s   0.029s age:MISS gender:OK
20_000007.v2.vad.wav               ERROR: HTTP 400: Audio must be at least 3 seconds.
 

audio_name	duration_sec	audeering_age_years_approx	audeering_age_bucket	mam_age	mam_age_confidence	age_bucket_match	audeering_gender	audeering_female_prob	audeering_male_prob	audeering_child_prob	mam_gender	mam_gender_confidence	gender_match	mam_gender_age	mam_gender_age_confidence	mam_age_gender_consistent	mam_models_available
audio-eng-happy.wav	6.1735	13.94797117	teens	twenties	0.990009725	FALSE	male	0.001740068	0.994640827	0.003619154	male	0.999046147	TRUE	female-fifties	0.451663405	FALSE	age,gender,gender_age
audio-eng-neutral.wav	7.9335	16.88743234	teens	twenties	0.898493052	FALSE	male	0.001164026	0.994766712	0.004069306	male	0.999487877	TRUE	male-fourties	0.830252826	FALSE	age,gender,gender_age
audio-eng-sad.wav	8.4535	19.8158294		twenties	0.936078668		male	0.00191849	0.994861662	0.003219732	male	0.998001635	TRUE	male-fourties	0.666972697	FALSE	age,gender,gender_age
audio-eng-surprised.wav	6.4535	25.55847764	twenties	twenties	0.998944104	TRUE	male	0.012077617	0.98686856	0.001053896	male	0.646933079	TRUE	male-twenties	0.533157766	TRUE	age,gender,gender_age
audio-tel-happy.wav	4.1335	15.08670002	teens	twenties	0.995948792	FALSE	male	0.003003764	0.993478179	0.003518025	male	0.747895479	TRUE	female-thirties	0.582529545	FALSE	age,gender,gender_age
audio-tel-neutral.wav	3.9135	15.68681151	teens	twenties	0.966881096	FALSE	male	0.000527712	0.992851555	0.006620714	male	0.9997769	TRUE	male-fourties	0.875005782	FALSE	age,gender,gender_age
audio-tel-sad.wav	5.8335	14.75990266	teens	twenties	0.947582722	FALSE	male	0.000554484	0.979479253	0.019966226	male	0.999697208	TRUE	male-fourties	0.827895105	FALSE	age,gender,gender_age
audio-tel-surprised.wav	5.4735	15.59443474	teens	twenties	0.944127738	FALSE	male	0.000584095	0.989642441	0.00977351	male	0.999194324	TRUE	male-twenties	0.644549251	TRUE	age,gender,gender_age