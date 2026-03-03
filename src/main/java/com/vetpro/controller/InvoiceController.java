package com.vetpro.controller;

import com.vetpro.model.Invoice;
import com.vetpro.service.InvoiceService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/invoices")
public class InvoiceController {

    private final InvoiceService invoiceService;

    public InvoiceController(InvoiceService invoiceService) {
        this.invoiceService = invoiceService;
    }

    @PostMapping
    public ResponseEntity<Invoice> createInvoice(@Valid @RequestBody Invoice invoice) {
        Invoice created = invoiceService.createInvoice(invoice);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Invoice> getInvoice(@PathVariable Long id) {
        return invoiceService.getInvoiceById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/owner/{ownerId}")
    public ResponseEntity<List<Invoice>> getByOwner(@PathVariable Long ownerId) {
        return ResponseEntity.ok(invoiceService.getInvoicesByOwner(ownerId));
    }

    @GetMapping("/unpaid")
    public ResponseEntity<List<Invoice>> getUnpaid() {
        return ResponseEntity.ok(invoiceService.getUnpaidInvoices());
    }

    @PutMapping("/{id}/pay")
    public ResponseEntity<Invoice> markAsPaid(@PathVariable Long id) {
        return ResponseEntity.ok(invoiceService.markAsPaid(id));
    }
}
