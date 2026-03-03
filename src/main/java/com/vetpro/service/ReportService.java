package com.vetpro.service;

import com.vetpro.model.Hospitalization;
import com.vetpro.model.Invoice;
import com.vetpro.model.Medication;
import com.vetpro.repository.AppointmentRepository;
import com.vetpro.repository.InvoiceRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class ReportService {

    private final AppointmentRepository appointmentRepository;
    private final InvoiceRepository invoiceRepository;
    private final MedicationService medicationService;
    private final HospitalizationService hospitalizationService;

    public ReportService(AppointmentRepository appointmentRepository,
                         InvoiceRepository invoiceRepository,
                         MedicationService medicationService,
                         HospitalizationService hospitalizationService) {
        this.appointmentRepository = appointmentRepository;
        this.invoiceRepository = invoiceRepository;
        this.medicationService = medicationService;
        this.hospitalizationService = hospitalizationService;
    }

    public long getAppointmentCountByDateRange(LocalDateTime start, LocalDateTime end) {
        return appointmentRepository.findByDateTimeBetween(start, end).size();
    }

    public BigDecimal getRevenueByDateRange(LocalDateTime start, LocalDateTime end) {
        return invoiceRepository.findAll().stream()
                .filter(Invoice::isPaid)
                .filter(inv -> !inv.getDateIssued().isBefore(start) && !inv.getDateIssued().isAfter(end))
                .map(Invoice::getTotalAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public List<Medication> getLowStockMedications() {
        return medicationService.getLowStockMedications();
    }

    public List<Hospitalization> getCurrentlyHospitalized() {
        return hospitalizationService.getCurrentlyAdmitted();
    }
}
