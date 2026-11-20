import pandas as pd
df = pd.read_csv('clock.tsv', sep='\t')
print(df)

# Filter in a variable for the login pc, we have found 165 as the stream of the sender
anchor = df[df["tcp.stream"] == 165]

# We search just for the anchor
first_time = min(anchor["frame.time_relative"])
print("Min time: ", first_time)
last_time = max(anchor["frame.time_relative"])
print("Max time: ", last_time)
first_tsval = min(anchor["tcp.options.timestamp.tsval"])
print("Min time: ", first_tsval)
last_tsval = max(anchor["tcp.options.timestamp.tsval"])
print("Max time: ", last_tsval)

hz = (last_tsval - first_tsval) / (last_time - first_time)
print("\nHZ: ", hz)
hz = min([100, 250, 1000], key=lambda h: abs(h - hz))
print("HZ snapped:", hz)

df['Costant'] = df['tcp.options.timestamp.tsval']-df['frame.time_relative']*hz
print(df)

grouped_stream = df.groupby("tcp.stream")["Costant"].median()
print(grouped_stream)

reference = grouped_stream[165]
print("Reference:", reference)

distance = (grouped_stream - reference).abs() / hz
print('Distance: ', distance.sort_values().head(30))

admin_streams = distance[distance < 1.0].index
print(admin_streams)
print(len(admin_streams))

#load all http requests
http = pd.read_csv('http.tsv', sep='\t')
print(http.columns)
print(len(http))
print(http.head())

# Check the admin sure output and we see the xtrace
print(http[http["tcp.stream"] == 165]["http.request.line"].iloc[0])

admin_http = http[http["tcp.stream"].isin(admin_streams)]
print(len(admin_http))
print(admin_http)

pattern = r"X-Trace: (\d)-([0-9a-f]{6})"

pieces = admin_http["http.request.line"].str.extract(pattern)
print(pieces)
#Part	Meaning
#X-Trace:	the literal text, matched exactly (including the space after the colon)
#(\d)	one digit, captured: this is n
#-	the literal dash
#([0-9a-f]{6})	exactly six hex characters, captured: this is the 6-character piece

# 1. Give the columns meaningful names (they were 0 and 1)
pieces.columns = ["n", "hex"]

# 2. Convert n from text to a number, so it sorts 1, 2, 3... correctly
pieces["n"] = pieces["n"].astype(int)

# 3. Remove duplicates: several streams carry the same piece
pieces = pieces.drop_duplicates()

# 4. Sort by piece number
pieces = pieces.sort_values("n")
print(pieces)

# 5. Check: exactly 8 pieces, one for each n from 1 to 8
print("Pieces:", len(pieces))
print("n values:", pieces["n"].tolist())

# 6. Join the 8 hex strings, in order, into one token
token = "".join(pieces["hex"])
print("Token length:", len(token))

# 7. Build the flag
print(f"netsec{{{token}}}")