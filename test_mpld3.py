import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 2, 3])
print(mpld3.fig_to_html(fig))
