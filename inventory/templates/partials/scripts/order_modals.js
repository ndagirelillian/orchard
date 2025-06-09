<script>
// ===================== EDIT STATUS MODAL =====================
const editOrderStatusModal = document.getElementById('editOrderStatusModal');

editOrderStatusModal.addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget;
  const orderId = button.getAttribute('data-order-id');
  const orderStatus = button.getAttribute('data-order-status');

  document.getElementById('modalOrderId').value = orderId;
  document.getElementById('modalOrderStatus').value = orderStatus;
});

const editStatusForm = document.getElementById('editOrderStatusForm');
if (editStatusForm) {
  editStatusForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const orderId = document.getElementById('modalOrderId').value;
    const status = document.getElementById('modalOrderStatus').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/manager/order/${orderId}/update-status/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ status: status })
    })
    .then(response => {
      if (response.ok) {
        bootstrap.Modal.getInstance(editOrderStatusModal).hide();
        location.reload();