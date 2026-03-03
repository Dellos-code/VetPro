package com.vetpro.service;

import com.vetpro.model.Invoice;
import com.vetpro.model.Payment;
import com.vetpro.repository.InvoiceRepository;
import com.vetpro.repository.PaymentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@Transactional
public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final InvoiceRepository invoiceRepository;

    public PaymentService(PaymentRepository paymentRepository, InvoiceRepository invoiceRepository) {
        this.paymentRepository = paymentRepository;
        this.invoiceRepository = invoiceRepository;
    }

    public Payment recordPayment(Payment payment) {
        Payment saved = paymentRepository.save(payment);
        Invoice invoice = saved.getInvoice();
        List<Payment> payments = paymentRepository.findByInvoiceId(invoice.getId());
        BigDecimal totalPaid = payments.stream()
                .map(Payment::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        if (totalPaid.compareTo(invoice.getTotalAmount()) >= 0) {
            invoice.setPaid(true);
            invoiceRepository.save(invoice);
        }
        return saved;
    }

    @Transactional(readOnly = true)
    public List<Payment> getPaymentsByInvoice(Long invoiceId) {
        return paymentRepository.findByInvoiceId(invoiceId);
    }
}
