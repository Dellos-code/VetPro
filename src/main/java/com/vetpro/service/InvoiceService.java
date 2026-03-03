package com.vetpro.service;

import com.vetpro.model.Invoice;
import com.vetpro.repository.InvoiceRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class InvoiceService {

    private final InvoiceRepository invoiceRepository;

    public InvoiceService(InvoiceRepository invoiceRepository) {
        this.invoiceRepository = invoiceRepository;
    }

    public Invoice createInvoice(Invoice invoice) {
        return invoiceRepository.save(invoice);
    }

    @Transactional(readOnly = true)
    public Optional<Invoice> getInvoiceById(Long id) {
        return invoiceRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public List<Invoice> getInvoicesByOwner(Long ownerId) {
        return invoiceRepository.findByOwnerId(ownerId);
    }

    @Transactional(readOnly = true)
    public List<Invoice> getUnpaidInvoices() {
        return invoiceRepository.findByPaidFalse();
    }

    public Invoice markAsPaid(Long id) {
        Invoice invoice = invoiceRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Invoice not found"));
        invoice.setPaid(true);
        return invoiceRepository.save(invoice);
    }
}
