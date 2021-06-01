const BASE_URL = window.location.href

document.querySelector('#countryBtn').addEventListener("click", function (evt) {
  evt.preventDefault();
  document.querySelector('#flash_messages').innerHTML = '';
  let value = document.querySelector('#countryInput').value;
  window.location.href = `/country/${value}`;
});

window.onload = async function (e) {
  canvas = document.querySelector('#covidChart');
  if (canvas) {
    const response = await axios.get(`${BASE_URL}/covid_data`);
    if (!response.data.error) {
      alert('no error')
      let ctx = canvas.getContext('2d');
      let covidChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: response.data.labels,
          datasets: [{
            label: 'Total cases over ~6 months',
            data: response.data.data,
            borderColor: [
              'rgba(255, 99, 132, 1)',
            ],
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)',
            ],
            borderWidth: 0.5
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero: true
              }
            }]
          }
        }
      });
    } else {
      canvas.parentNode.replaceChild(document.createTextNode(response.data.error), canvas)
    }
  }
}