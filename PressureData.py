from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator

data = pd.read_excel(r"Reservoir_Pressure_Data_Student_Updated.xlsx")
data['STUDY_DATE'] = pd.to_datetime(data['STUDY_DATE'])
data['FIELD_NAME'] = data['WELL_NAME'].str[:4]

sands = ["All"] + sorted(data['SAND'].unique())
fields = ["All"] + sorted(data['FIELD_NAME'].unique())
wells = ["All"] + sorted(data['WELL_NAME'].unique())

root = Tk()
root.title("RESERVOIR PRESSURE")
root.geometry("1200x900")
root.configure(bg="#AD49E1")

selection = IntVar(value=0)
selected_sand = StringVar(value="All")
selected_field = StringVar(value="All")
selected_well = StringVar(value="All")

def update_well_options(*args):
    if selection.get() == 0: 
        sand_dropdown.configure(state="readonly")  
        field_dropdown.configure(state="disabled") 
        if selected_sand.get() == "All":
            wells_list = ["All"] + sorted(data['WELL_NAME'].unique())
        else:
            wells_list = ["All"] + sorted(data[data['SAND'] == selected_sand.get()]['WELL_NAME'].unique())
    else: 
        field_dropdown.configure(state="readonly") 
        sand_dropdown.configure(state="disabled")
        if selected_field.get() == "All":
            wells_list = ["All"] + sorted(data['WELL_NAME'].unique())
        else:
            wells_list = ["All"] + sorted(data[data['FIELD_NAME'] == selected_field.get()]['WELL_NAME'].unique())
    well_dropdown['values'] = wells_list
    selected_well.set("All")

def plot():
    filtered_data = data.copy()
    title_filter = "SAND"
    title_value = selected_sand.get()
    title_well = ""

    if selection.get() == 0:  
        if selected_sand.get() != "All":
            filtered_data = filtered_data[filtered_data['SAND'] == selected_sand.get()]
    else:  
        title_filter = "FIELD"
        title_value = selected_field.get()
        if selected_field.get() != "All":
            filtered_data = filtered_data[filtered_data['FIELD_NAME'] == selected_field.get()]

    if selected_well.get() != "All":
        filtered_data = filtered_data[filtered_data['WELL_NAME'] == selected_well.get()]
        title_well = f", WELL: {selected_well.get()}"

    for widget in f2.winfo_children():
        widget.destroy()

    if filtered_data.empty:
        fig, ax = plt.subplots(figsize=(13.8, 8.3))
        ax.text(0.5, 0.5, 'No Records\nAvailable', fontsize=45, ha='center', va='center', color='gray', fontname='Verdana Rounded MT Bold')
        ax.axis('off')
    else:
        filtered_data = filtered_data.sort_values(by='STUDY_DATE', ascending=True)
        filtered_data['STUDY_DATE'] = filtered_data['STUDY_DATE'].dt.strftime('%d-%b-%y')
        
        fig, ax = plt.subplots(figsize=(13.8, 8.3))
        plt.subplots_adjust(left=0.069, right=0.97, top=0.926, bottom=0.17)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=20))
        ax.set_ylim(0, filtered_data['BH_PRESSURE'].max()+15)

        r_copper = sns.color_palette("copper", as_cmap=True).reversed()
        bar = sns.barplot(ax=ax, data=filtered_data, x='STUDY_DATE', y='BH_PRESSURE', hue='WELL_NAME', palette='deep',zorder=2,linewidth=1.5, edgecolor='white')
        sns.scatterplot(ax=ax, data=filtered_data, x='STUDY_DATE', y='BH_PRESSURE', hue='BEAN_SIZE',s=120, palette=r_copper, legend='brief', linewidth=1.5, edgecolor='white',zorder=1)

    for y in ax.get_yticks():
        ax.axhline(y=y, color='#e8e6e6', linewidth=16, zorder=0)
        
        handles, labels = ax.get_legend_handles_labels()
        legend_well = ax.legend(handles[:len(filtered_data['WELL_NAME'].unique())], labels[:len(filtered_data['WELL_NAME'].unique())], title="Well Name", loc='upper right', fontsize=10)
        ax.add_artist(legend_well)
        legend_bean = ax.legend(handles[len(filtered_data['WELL_NAME'].unique()):], labels[len(filtered_data['WELL_NAME'].unique()):], title="Bean Size", loc='upper left', fontsize=10)
        
        plt.title(f"Bottom Hole Pressure for {title_filter}: {title_value}{title_well}", fontsize=18, fontname='Arial Rounded MT Bold')
        plt.xlabel("Date of Testing", fontsize=13, fontname='Arial Rounded MT Bold')
        plt.ylabel("Bottom Hole Pressure (kg/cm²)", fontsize=13, fontname='Arial Rounded MT Bold')
        plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=f2)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, f2)
    toolbar.update()
    toolbar.pack(side=TOP, fill=X)
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

f1 = Frame(root, bg="#2E073F", bd=5)
f1.pack(fill=X)

f2 = Frame(root, bg="#ffffff", bd=5, relief=RIDGE)
f2.pack(fill=BOTH, expand=True, padx=5, pady=5)

Label(f1, text="-----------------------   ONGC RESERVOIR PRESSURE DATA TRIPURA ASSET   -----------------------", font=("Arial Rounded MT Bold", 30), bg="#2E073F", fg="white").pack(pady=10)

controls_frame = Frame(f1, bg="#b304bf", bd=3, relief=RAISED)
controls_frame.pack(pady=10)

Radiobutton(controls_frame, text="Sand", variable=selection, value=0, font=("Verdana", 12), bg="#fccfff", fg="Black", command=update_well_options, relief=RAISED).grid(row=0, column=0, padx=10, pady=10)
Radiobutton(controls_frame, text="Field Name", variable=selection, value=1, font=("Verdana", 12), bg="#fccfff", fg="Black", command=update_well_options, relief=RAISED).grid(row=0, column=1, padx=10, pady=10)

Label(controls_frame, text="Select Sand:", font=("Verdana", 12), bg="#2E073F", fg="white", relief=RAISED).grid(row=1, column=0, padx=10, pady=5)
sand_dropdown = ttk.Combobox(controls_frame, values=sands, textvariable=selected_sand, font=("Verdana", 12), state="readonly", width=20)
sand_dropdown.grid(row=1, column=1, padx=10, pady=5)
sand_dropdown.bind("<<ComboboxSelected>>", update_well_options)

Label(controls_frame, text="Select Field:", font=("Verdana", 12), bg="#2E073F", fg="white", relief=RAISED).grid(row=2, column=0, padx=5, pady=5)
field_dropdown = ttk.Combobox(controls_frame, values=fields, textvariable=selected_field, font=("Verdana", 12), state="disabled", width=20)
field_dropdown.grid(row=2, column=1, padx=5, pady=5)
field_dropdown.bind("<<ComboboxSelected>>", update_well_options)

Label(controls_frame, text="Select Well:", font=("Verdana", 12), bg="#2E073F", fg="white", relief=RAISED).grid(row=3, column=0, padx=5, pady=5)
well_dropdown = ttk.Combobox(controls_frame, values=wells, textvariable=selected_well, font=("Verdana", 12), state="readonly", width=20)
well_dropdown.grid(row=3, column=1, padx=5, pady=5)

Button(controls_frame, text="SUBMIT", command=plot, font=("Verdana", 12, "bold"), bg="#2E073F", fg="white", width=10, relief=RAISED).grid(row=4, column=1, padx=10, pady=10)

update_well_options()
root.mainloop()
